from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel, Field 
from app.database import get_connection
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timezone, timedelta
from app import config
import bcrypt
import jwt
import os


router = APIRouter(prefix="/users")

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
  username: str = Field(min_length=1, max_length=16, pattern=r"^[a-zA-Z]+$")
  password: str 

@router.post("/register")
def register(user: User):
  with get_connection() as connection:
    row = connection.execute(
        "SELECT id FROM users WHERE username = ?",(user.username,)
    ).fetchone()

    if row is not None:
      raise HTTPException(status_code=409, detail="Username already exist")

    hashed = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    connection.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (user.username, hashed.decode("utf-8"))
    )
    connection.commit()

  return Response(status_code=201)


@router.post("/login")
def login(user: User):
  with get_connection() as connection:
    row = connection.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",(user.username,)
    ).fetchone()

    if row is None:
      raise HTTPException(status_code=401, detail="Wrong password or wrong username, verify data")

    stored_hash = row["password_hash"].encode("utf-8")
    if not bcrypt.checkpw(user.password.encode("utf-8"), stored_hash):
        raise HTTPException(status_code=401, detail="Wrong password or wrong username, verify data")

    with open(config.PRIVATE_KEY_PATH, 'r') as f:
      private_key = f.read()
    
    key = serialization.load_pem_private_key(private_key.encode(), password=os.environ["SECRET_PHRASE"].encode())

    payload_data = {
        "sub": str(row["id"]),
        "username": row["username"],
        "exp": datetime.now(tz=timezone.utc)+timedelta(minutes=15)
    }

    session_token = jwt.encode(
        payload=payload_data,
        key=key,
        algorithm='RS256'
    )
      
    return Token(access_token=session_token, token_type="bearer")

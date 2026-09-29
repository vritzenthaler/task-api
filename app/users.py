from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel, Field, field_validator
import re
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

class UserRegistration(BaseModel):
  username: str = Field(min_length=1, max_length=16, pattern=r"^[a-zA-Z]+$")
  password: str = Field(min_length=8, max_length=32)

  @field_validator("password")
  @classmethod
  def check_password_strength(cls, v: str) -> str:

    errors = []
    if not re.search(r"[a-z]", v):
      errors.append("a lowercase letter")
    if not re.search(r"[A-Z]", v):
      errors.append("an uppercase letter")
    if not re.search(r"\d", v):
      errors.append("a digit")
    if not re.search(r"[^\w\s]", v):
      errors.append("a special character")
    if not v.isascii():
      errors.append("only ASCII characters")
    if errors:
      raise ValueError("Must contain " + ", ".join(errors))

    return v

class UserLogin(BaseModel):
  username: str = Field(min_length=1, max_length=32)
  password: str = Field(min_length=1, max_length=32)

  @field_validator("password")
  @classmethod
  def check_password(cls, v: str) -> str:

    if not v.isascii():
      raise ValueError("Wrong password")

    return v


@router.post("/register")
def register(user: UserRegistration):
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
def login(user: UserLogin):
  with get_connection() as connection:
    row = connection.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",(user.username,)
    ).fetchone()

    if row is None:
      raise HTTPException(status_code=401, detail="Wrong password or wrong username")

    stored_hash = row["password_hash"].encode("utf-8")
    if not bcrypt.checkpw(user.password.encode("utf-8"), stored_hash):
        raise HTTPException(status_code=401, detail="Wrong password or wrong username")

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

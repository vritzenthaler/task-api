from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Response, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field 
from app.database import init_db, DB_PATH, get_connection
from app.users import router
from app import config
from jwt.exceptions import InvalidTokenError
from cryptography.hazmat.primitives import serialization
import jwt
from typing import Annotated

ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Task API", lifespan=lifespan)
app.include_router(router)

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=16, pattern=r"^[a-zA-Z]+$")

class TaskUpdate(BaseModel):
    done: bool | None = None
    title: str | None = Field(default=None, min_length=1, max_length=16, pattern=r"^[a-zA-Z]+$")

class Task(TaskCreate):
    id: int
    done: bool = False

def auth_check(token: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        with open(config.PUBLIC_KEY_PATH, 'r') as f:
            public_key_pem = f.read()
        pub_key = serialization.load_pem_public_key(public_key_pem.encode())
        payload = jwt.decode(token.credentials, pub_key, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    return user_id

@app.get("/tasks", response_model=list[Task])
def list_tasks(token: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    user_id = auth_check(token)

    with get_connection() as connection:
        user = connection.execute(
            "SELECT id, username FROM users WHERE id = ?",(int(user_id),)
        ).fetchone()

        if user is None:
            raise HTTPException(status_code=404, detail="Could not validate user")

        rows = connection.execute(
            "SELECT id, title, done FROM tasks WHERE user_id = ? ORDER BY id",(int(user_id),),
        ).fetchall()

    return [
        Task(id=row["id"], title=row["title"], done=bool(row["done"]))
        for row in rows
    ]

@app.post("/tasks", response_model=Task, status_code=201)
def create_task(data: TaskCreate, token: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    user_id = auth_check(token)

    with get_connection() as connection:
        user = connection.execute(
            "SELECT id, username FROM users WHERE id = ?",(int(user_id),)
        ).fetchone()

        if user is None:
            raise HTTPException(status_code=404, detail="Could not validate user")
    
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO tasks (title,user_id) VALUES(?,?)",(data.title,user_id)
        )
        connection.commit()
        task_id = cursor.lastrowid

    task = Task(id=task_id, title=data.title, done=False)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, token: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    user_id = auth_check(token)

    with get_connection() as connection:
        user = connection.execute(
            "SELECT id, username FROM users WHERE id = ?",(int(user_id),)
        ).fetchone()

        if user is None:
            raise HTTPException(status_code=404, detail="Could not validate user")

        row = connection.execute(
            "SELECT user_id FROM tasks WHERE id = ?",(task_id,)
        ).fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Invalid task, can't be deleted")

        if row["user_id"] != int(user_id):
            raise HTTPException(status_code=404, detail="Invalid task, can't be deleted")

        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?",(task_id,)
        )

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task id does not exist")

        connection.commit()
    
    return Response(status_code=204)

@app.patch("/tasks/{task_id}", response_model=Task)
def patch_task(task_id: int, data: TaskUpdate, token: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    user_id = auth_check(token)

    changes = data.model_dump(exclude_unset=True)

    if any(value is None for value in changes.values()):
        raise HTTPException(status_code=422, detail="Fields cannot be None")

    with get_connection() as connection:
        user = connection.execute(
            "SELECT id, username FROM users WHERE id = ?",(int(user_id),)
        ).fetchone()

        if user is None:
            raise HTTPException(status_code=404, detail="Could not validate user")

        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ? AND user_id = ?",(task_id,user_id)
        ).fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Invalid task id")

        task = Task(id=row["id"], title=row["title"], done=bool(row["done"]))

        if "title" in changes:
            connection.execute(
                "UPDATE tasks SET title = ? WHERE id = ? AND user_id = ?",(changes.get("title"),task_id,int(user_id))
            )
        if "done" in changes:
            connection.execute(
                "UPDATE tasks SET done = ? WHERE id = ? AND user_id = ?",(changes.get("done"),task_id,int(user_id))
            )

        connection.commit()
        return task.model_copy(update=changes)


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int, token: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    user_id = auth_check(token)

    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ? AND user_id = ?",
            (task_id,user_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return Task(
        id=row["id"],
        title=row["title"],
        done=bool(row["done"]),
    )

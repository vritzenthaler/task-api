# Task API

Task management API built with FastAPI, SQLite, bcrypt, and RS256 JWT authentication. Each user can access only their own tasks.

## Installation

Python 3.10 or later (developed with Python 3.12) and `uv` are required. From the project root:

```bash
uv sync --extra dev --locked
uv run python scripts/setup_local.py
uv run uvicorn app.main:app --reload
```

The script creates a new RSA key pair in `.keys/` and a random secret in `.env`. It will not overwrite an existing configuration. `.env.example` documents the variable used. No accounts, keys, or database are included with the project.

SQLite creates `app_database.db` at startup. Interactive documentation: http://127.0.0.1:8000/docs.

## Usage

1. Create an account with `POST /users/register`, for example `{"username": "alice", "password": "your-password"}`.
2. Log in with `POST /users/login` using the same credentials.
3. Provide `access_token` in `Authorization: Bearer <token>`. In `/docs`, click **Authorize**.

Tokens expire after 15 minutes. Usernames and task titles must contain 1 to 16 ASCII letters, with no spaces or digits.

| Method | Route | Description |
| --- | --- | --- |
| POST | `/users/register` | Register |
| POST | `/users/login` | Log in |
| GET | `/tasks` | List tasks |
| POST | `/tasks` | Create a task with `{"title": "Example"}` |
| GET | `/tasks/{task_id}` | Retrieve a task |
| PATCH | `/tasks/{task_id}` | Update `title` and/or `done` |
| DELETE | `/tasks/{task_id}` | Delete a task |

## Tests

```bash
uv run --extra dev pytest
```

Les tests génèrent une base SQLite et des clés JWT temporaires. Ils fonctionnent sans `.env` ni configuration locale préalable.

## Dependencies

Dependencies are declared in `pyproject.toml`; `uv.lock` pins their versions. After changing dependencies, run `uv lock`. No separate `requirements.txt` is maintained.

## New repository

Git is initialized on `main`, with no imported history or remote. After creating an empty remote repository:

```bash
git add .
git commit -m "Initial Task API extraction"
git remote add origin <REPOSITORY_URL>
git push -u origin main
```

Secrets, keys, local databases, virtual environments, and caches are excluded by `.gitignore`.

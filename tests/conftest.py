from fastapi.testclient import TestClient
import pytest

from app import main, database, config
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


@pytest.fixture(scope="session")
def jwt_keys(tmp_path_factory):
    key_dir = tmp_path_factory.mktemp("jwt")
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private = key_dir / "private.pem"
    public = key_dir / "public.pem"
    private.write_bytes(key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
        serialization.BestAvailableEncryption(b"test-only-passphrase"),
    ))
    public.write_bytes(key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo,
    ))
    return private, public


@pytest.fixture(autouse=True)
def isolated_jwt(jwt_keys, monkeypatch):
    monkeypatch.setattr(config, "PRIVATE_KEY_PATH", jwt_keys[0])
    monkeypatch.setattr(config, "PUBLIC_KEY_PATH", jwt_keys[1])
    monkeypatch.setenv("SECRET_PHRASE", "test-only-passphrase")


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db_path = tmp_path / "test_tasks.db"

    # L'API et init_db doivent utiliser la même base temporaire.
    monkeypatch.setattr(main, "DB_PATH", test_db_path)
    monkeypatch.setattr(database, "DB_PATH", test_db_path)

    with TestClient(main.app) as test_client:
        yield test_client

@pytest.fixture
def auth_headers_alice(client):
    register_response = client.post("/users/register", json={"username": "alice", "password": "Il0v3y0u*"})
    assert register_response.status_code == 201, register_response.text

    login_response = client.post("/users/login", json={"username": "alice", "password": "Il0v3y0u*"})
    assert login_response.status_code == 200, login_response.text

    token = login_response.json()["access_token"]
    headers = {'Authorization': f'Bearer {token}'}

    return headers

@pytest.fixture
def auth_headers_bob(client):
    register_response = client.post("/users/register", json={"username": "bob", "password": "Il0v3y0u*"})
    assert register_response.status_code == 201, register_response.text

    login_response = client.post("/users/login", json={"username": "bob", "password": "Il0v3y0u*"})
    assert login_response.status_code == 200, login_response.text

    token = login_response.json()["access_token"]
    headers = {'Authorization': f'Bearer {token}'}

    return headers

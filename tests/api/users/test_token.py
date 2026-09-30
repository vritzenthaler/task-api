import jwt 
from datetime import datetime, timezone, timedelta
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import os

ALGORITHM = 'RS256'

def test_expired_token(client,auth_headers_alice,jwt_keys):
    valid_token = auth_headers_alice["Authorization"].removeprefix("Bearer ")

    with open(jwt_keys[1], 'r') as f:
        public_key_pem = f.read()
    pub_key = serialization.load_pem_public_key(public_key_pem.encode())
    payload = jwt.decode(valid_token, pub_key, algorithms=[ALGORITHM])

    with open(jwt_keys[0], 'r') as f:
        private_key_pem = f.read()
    key = serialization.load_pem_private_key(private_key_pem.encode(), password=os.environ["SECRET_PHRASE"].encode())

    payload_data = {
        "sub": payload["sub"],
        "username": payload["username"],
        "exp": datetime.now(tz=timezone.utc)-timedelta(minutes=1)
    }

    token = jwt.encode(
        payload=payload_data,
        key=key,
        algorithm=ALGORITHM
    )

    expired_headers = {'Authorization': f'Bearer {token}'}

    get_response = client.get("/tasks", headers=expired_headers)
    assert get_response.status_code == 401
    assert get_response.json()["detail"] == "Expired Token"

def test_invalid_signature(client,auth_headers_alice,jwt_keys):
    valid_token = auth_headers_alice["Authorization"].removeprefix("Bearer ")

    with open(jwt_keys[1], 'r') as f:
        public_key_pem = f.read()
    pub_key = serialization.load_pem_public_key(public_key_pem.encode())
    payload = jwt.decode(valid_token, pub_key, algorithms=[ALGORITHM])

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    payload_data = {
        "sub": payload["sub"],
        "username": payload["username"],
        "exp": datetime.now(tz=timezone.utc)+timedelta(minutes=15)
    }

    token = jwt.encode(
        payload=payload_data,
        key=key,
        algorithm=ALGORITHM
    )

    invalid_headers = {'Authorization': f'Bearer {token}'}

    get_response = client.get("/tasks", headers=invalid_headers)
    assert get_response.status_code == 401
    assert get_response.json()["detail"] == "Could not validate credentials"
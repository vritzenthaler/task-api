"""Generate local JWT keys and configuration without overwriting existing files."""
from pathlib import Path
import os
import secrets
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

root = Path(__file__).resolve().parent.parent
key_dir = root / ".keys"
paths = [root / ".env", key_dir / "jwt-private.pem", key_dir / "jwt-public.pem"]
if any(path.exists() for path in paths):
    raise SystemExit("Configuration already exists; no files changed.")
phrase = secrets.token_urlsafe(32)
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
key_dir.mkdir(mode=0o700, exist_ok=True)
contents = [
    ("SECRET_PHRASE=" + phrase + "\n").encode(),
    key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                      serialization.BestAvailableEncryption(phrase.encode())),
    key.public_key().public_bytes(serialization.Encoding.PEM,
                                 serialization.PublicFormat.SubjectPublicKeyInfo),
]
for path, content in zip(paths, contents):
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as file:
        file.write(content)
print("Local .env and JWT keys created. Keep these files private.")

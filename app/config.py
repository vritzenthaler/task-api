from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
PRIVATE_KEY_PATH = ROOT / ".keys/jwt-private.pem"
PUBLIC_KEY_PATH = ROOT / ".keys/jwt-public.pem"

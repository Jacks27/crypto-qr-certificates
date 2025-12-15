# crypto_utils.py
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os, json, base64
from dotenv import load_dotenv

load_dotenv()

def get_key() -> bytes:
    key_str = os.getenv("ENCRYPTION_KEY")
    if not key_str:
        raise ValueError("ENCRYPTION_KEY not set in .env")
    
    # Support both hex and base64
    try:
        if len(key_str) == 64:  # hex
            return bytes.fromhex(key_str)
        else:  # assume base64
            return base64.b64decode(key_str)
    except Exception as e:
        raise ValueError("Invalid ENCRYPTION_KEY format. Use 64-char hex or base64.") from e

def encrypt_payload(payload: dict) -> str:
    key = get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    data = json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode("utf-8")
    ct = aesgcm.encrypt(nonce, data, None)
    token = base64.urlsafe_b64encode(nonce + ct).decode().rstrip("=")
    return token

def decrypt_payload(token: str) -> dict:
    key = get_key()
    aesgcm = AESGCM(key)
    raw = base64.urlsafe_b64decode(token + "===")
    nonce, ct = raw[:12], raw[12:]
    data = aesgcm.decrypt(nonce, ct, None)
    return json.loads(data)
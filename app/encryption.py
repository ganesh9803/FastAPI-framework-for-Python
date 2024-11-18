# app/encryption.py
import jwt
from datetime import datetime, timedelta
from app.config import SECRET_KEY, ALGORITHM

def create_encrypted_url(file_id: int) -> str:
    expiration = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode({"file_id": file_id, "exp": expiration}, SECRET_KEY, algorithm=ALGORITHM)

def verify_encrypted_url(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("file_id")
    except jwt.ExpiredSignatureError:
        return None
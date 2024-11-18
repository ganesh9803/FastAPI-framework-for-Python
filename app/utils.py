# app/utils.py
from datetime import datetime, timedelta
import jwt
from app.config import SECRET_KEY, ALGORITHM

def create_encrypted_url(user_id: int) -> str:
    expiration = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode({"user_id": user_id, "exp": expiration}, SECRET_KEY, algorithm=ALGORITHM)

def verify_encrypted_url(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        return None
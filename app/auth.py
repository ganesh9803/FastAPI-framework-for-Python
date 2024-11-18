# app/auth.py
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
import jwt
from app.config import SECRET_KEY, ALGORITHM
from fastapi import HTTPException
from app.models import User
from app.database import SessionLocal
from functools import wraps
from fastapi import Request


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload if payload["exp"] >= datetime.utcnow().timestamp() else None
    except jwt.PyJWTError:
        return None

def authenticate_user(db: SessionLocal, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None


def role_required(required_role: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            token = request.headers.get("Authorization").split(" ")[1]
            payload = verify_access_token(token)

            if not payload or (required_role == "ops" and not payload.get("is_ops_user")):
                raise HTTPException(status_code=403, detail="Permission denied")

            return await func(*args, **kwargs)
        return wrapper
    return decorator

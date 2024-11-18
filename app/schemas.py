#app/schemas.py
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class FileCreate(BaseModel):
    file_name: str

class UserCreateOps(UserCreate):  
    
    pass
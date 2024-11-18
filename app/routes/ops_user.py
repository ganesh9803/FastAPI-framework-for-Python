# app/routes/ops_user.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.auth import create_access_token,hash_password,verify_password
from datetime import timedelta
from app.schemas import UserLogin,UserCreateOps
from datetime import datetime
import os
from app.database import get_db
from app.models import File as DbFile, User

router = APIRouter()

@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # Fetch the user by email and check if the user is an ops user
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate JWT token upon successful login
    access_token = create_access_token(
        data={"sub": user.email},  # 'sub' is a standard claim for the subject of the token
        expires_delta=timedelta(minutes=60)  # Token expiration time (1 hour)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/signup")
def signup(user_data: UserCreateOps, db: Session = Depends(get_db)):
    # Check if the email is already registered
    user = db.query(User).filter(User.email == user_data.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    hashed_password = hash_password(user_data.password)

    # Create the new user with is_ops_user set to True
    new_user = User(email=user_data.email, hashed_password=hashed_password, is_ops_user=True)

    # Save to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Ops User created successfully"}


@router.post("/upload")
def upload_file(uploaded_file: UploadFile = File(...), db: Session = Depends(get_db)):
    allowed_types = [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    ]
    if uploaded_file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Ensure the uploads directory exists
    os.makedirs("uploads", exist_ok=True)

    # Save the file with a unique filename to avoid collisions
    file_path = f"uploads/{uploaded_file.filename}"
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.file.read())

    # Set the uploaded_role as "ops" for Ops users
    uploaded_role = "ops"

    # Store file information in the database
    db_file = DbFile(file_name=uploaded_file.filename, file_path=file_path, uploaded_role=uploaded_role)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)  # Refresh to get the file_id

    return {
        "message": "File uploaded successfully",
        "file_id": db_file.id,  # Return the file ID
        "file_name": db_file.file_name
    }

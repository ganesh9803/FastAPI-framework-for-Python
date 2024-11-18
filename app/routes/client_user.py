# app/routes/client_user.py
from fastapi import APIRouter, Depends, HTTPException, File
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from app.auth import create_access_token,hash_password,verify_password
from datetime import timedelta
from app.schemas import UserLogin,UserCreate
import os
from app.database import get_db
from app.email import send_verification_email
from app.models import File as DbFile, User
from app.models import File
from urllib.parse import quote_plus
from app.utils import verify_encrypted_url
from urllib.parse import unquote
from fastapi.responses import FileResponse


router = APIRouter()

@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # Retrieve the user from the database
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if the email is verified
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Please verify your email first.")
    
    # Verify the password
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate an access token upon successful login
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=60)  # 1-hour token expiration
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/signup")
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if the user email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password and create a new user entry with `is_verified=False`
    hashed_password = hash_password(user_data.password)
    pending_user = User(email=user_data.email, hashed_password=hashed_password, is_verified=False)
    db.add(pending_user)
    db.commit()

    # Send email verification link
    send_verification_email(user_data.email, pending_user.id)
    
    return {"message": "User registered. Please check your email to verify your account."}



@router.get("/verify/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    # Decode and validate the encrypted token
    user_id = verify_encrypted_url(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Retrieve the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update the user's `is_verified` status
    user.is_verified = True
    db.commit()
    
    return {"message": "Email verified successfully! You can now log in."}


@router.get("/download/{file_id}")
def generate_download_link(file_id: int, db: Session = Depends(get_db)):
    # Fetch the file record from the database
    file = db.query(DbFile).filter(DbFile.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Construct and sanitize file path
    file_path = file.file_path.strip()
    full_file_path = os.path.join(os.getcwd(), file_path)
    if not os.path.exists(full_file_path):
        raise HTTPException(status_code=404, detail="File not found on server")
    
    # Generate and return the download link
    download_link = f"http://127.0.0.1:8000/client/download-file/{quote_plus(file_path)}"
    return {
        "message": "success",
        "download-link": download_link
    }
@router.get("/files")
def get_uploaded_files(db: Session = Depends(get_db)):
    """
    Fetch all files uploaded by Ops Users.
    This endpoint is accessible to client users after login.
    """
    files = db.query(DbFile).all()

    if not files:
        raise HTTPException(status_code=404, detail="No files found")

    # Return file details, excluding sensitive paths
    return [
        {
            "file_id": file.id,
            "file_name": file.file_name
        }
        for file in files
    ]


@router.get("/download-file/{file_path:path}")
def download_file(file_path: str, db: Session = Depends(get_db)):
    # Decode the file path (e.g., %2F should be converted back to '/')
    decoded_file_path = unquote(file_path)

    # Construct the full file path on the server
    full_file_path = os.path.join(os.getcwd(), decoded_file_path)

    # Check if the file exists
    if not os.path.exists(full_file_path):
        raise HTTPException(status_code=404, detail="File not found on server")

    # Return the file response
    return FileResponse(full_file_path)

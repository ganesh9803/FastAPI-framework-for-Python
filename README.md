# Secure File Sharing System

This is a FastAPI-based secure file sharing system with role-based access control, where there are two types of users: **Ops Users** and **Client Users**.

- **Ops Users**: Can upload files and view the uploaded files.
- **Client Users**: Can sign up, verify their email, and download files uploaded by Ops users.

## Features

- **User Authentication**: Email verification and login with JWT tokens.
- **Role-based Access Control**: Differentiates between Ops Users and Client Users.
- **File Upload and Download**:
  - Ops Users can upload files of specific types (pptx, docx, xlsx).
  - Client Users can download files via encrypted URLs.
- **Email Verification**: Sent after user signup for email verification.
- **Encrypted URLs**: For secure file download links.
- **Database**: PostgreSQL using SQLAlchemy.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (via SQLAlchemy)
- **Authentication**: JWT with password hashing via `passlib`
- **File Upload**: Supports pptx, docx, and xlsx files.
- **Email Service**: SMTP for email verification.

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL Database
- `.env` file for environment variables

### Steps to Setup

### Install dependencies

- pip install -r requirements.txt

### Create a .env file

 DATABASE_URL=postgresql://user:password@localhost/yourdbname
 SECRET_KEY=your-secret-key
 SMTP_USER=your-smtp-username
 SMTP_PASSWORD=your-smtp-password
 SMTP_SERVER=smtp.your-email-provider.com
 SMTP_PORT=587

### Run the application

 - uvicorn app.main:app --reload

 ### folder structure

├── app
│   ├── auth.py              # Authentication utilities (hashing, JWT)
│   ├── database.py          # Database connection and models
│   ├── email.py             # Email sending utility
│   ├── encryption.py        # URL encryption and decryption
│   ├── main.py              # FastAPI app setup
│   ├── models.py            # Database models (User, File)
│   ├── routes/               # API routes (client_user.py, ops_user.py)
│   ├── schemas.py           # Pydantic models for request/response
│   └── utils.py             # Utility functions
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── README.md                # This file

# API endpoints

To start server: uvicorn app.main:app --reload

client
1.POST http://127.0.0.1:8000/client/signup

2.POST http://127.0.0.1:8000/client/login

3.GET http://127.0.0.1:8000/client/files
  
  Authorization : Bearer 
  

4.GET http://127.0.0.1:8000/client/download/

5 GET http://127.0.0.1:8000/client/download-file/{file_path}



Operation User
1.POST http://127.0.0.1:8000/ops/signup

2.POST http://127.0.0.1:8000/ops/login

3.POST http://127.0.0.1:8000/ops/upload

   Authorization : Bearer



1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/secure-file-sharing-system.git
   cd secure-file-sharing-system

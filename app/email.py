# app/email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException
from app.utils import create_encrypted_url  # Your custom utility for encryption
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def send_verification_email(user_email: str, user_id: int):
    encrypted_url = create_encrypted_url(user_id)
    verification_url = f"http://127.0.0.1:8000/client/verify/{encrypted_url}"

    # Get SMTP configuration from environment variables
    sender_email = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")  # Load SMTP server from .env

    subject = "Email Verification"
    body = f"Please click the link to verify your email: {verification_url}"

    # Define the receiver email (it should be the user email provided)
    receiver_email = user_email

    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        # Connect to the SMTP server (TLS)
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()  # Secure connection
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Verification email sent successfully!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {e}")

#app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import client_user, ops_user
from app.database import engine, Base
from app.routes import client_user, ops_user

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include routers for client and ops users
app.include_router(client_user.router, prefix="/client", tags=["Client User"])
app.include_router(ops_user.router, prefix="/ops", tags=["Ops User"])

# Serve the uploads directory via StaticFiles, so files are accessible
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def read_root():
    return {"message": "Welcome to the secure file sharing system!"}

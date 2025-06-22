from fastapi import FastAPI
from sqlmodel import SQLModel
from app.db import engine
from app.api import device, log
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from pathlib import Path

# This is the correct, robust way to find the .env file.
# It finds the directory of this file (main.py), goes up one level to the project root,
# and then finds the .env file there.
current_dir = Path(__file__).parent
project_root = current_dir.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

app = FastAPI()

# Get allowed origins from environment variable
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(',') if origin]

# A print statement to see what origins are actually loaded.
print("--- FastAPI starting up (Corrected version) ---")
if os.path.exists(env_path):
    print(f"Found .env file at: {env_path}")
else:
    print(f"Warning: .env file not found at {env_path}. Using defaults.")
print(f"Loaded ALLOWED_ORIGINS: {allowed_origins}")
print("---------------------------------------------")

app.add_middleware(
       CORSMiddleware,
       allow_origins=allowed_origins,
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(device.router, prefix="/api")
app.include_router(log.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to the IoT Device API"}
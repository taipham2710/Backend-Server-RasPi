from fastapi import FastAPI
from sqlmodel import SQLModel
from app.db import engine
from app.api import device, log
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

app = FastAPI()

# Get allowed origins from environment variable
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(',') if origin]

# If no origins are specified, you might want to default to something for development
if not allowed_origins:
    allowed_origins = ["http://localhost:3000", "http://localhost:3001"]

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
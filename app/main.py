from fastapi import FastAPI
from sqlmodel import SQLModel
from app.db import engine
from app.api import device, log

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(device.router)
app.include_router(log.router)

@app.get("/")
def root():
    return {"message": "Welcome to the IoT Device API"}
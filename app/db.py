from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment variable, with a default value
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///iot.db")

engine = create_engine(DATABASE_URL, echo=False)

def get_session():
    with Session(engine) as session:
        yield session
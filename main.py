from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Field, Session, create_engine, select
from contextlib import asynccontextmanager
from typing import Optional, List
from datetime import datetime

app = FastAPI()
engine = create_engine("sqlite:///iot.db")

class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    last_seen: datetime = Field(default_factory=datetime.utcnow)

class Log(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: int = Field(foreign_key="device.id")
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

def get_session():
    with Session(engine) as session:
        yield session

@app.get("/")
async def root():
    return {"message": "Welcome to the IoT Device API"}

@app.post("/log")
async def receive_log(log: Log, session: Session = Depends(get_session)):
    # check if the device exists
    device = session.get(Device, log.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    session.add(log)
    session.commit()
    return {"status": "ok"}

@app.get("/devices", response_model=List[Device])
def list_devices(session: Session = Depends(get_session)):
    return session.exec(select(Device)).all()

@app.post("/device/heartbeat")
async def heartbeat(device: Device, session: Session = Depends(get_session)):
    d = session.exec(select(Device).where(Device.name == device.name)).first()
    if d:
        d.last_seen = datetime.utcnow()
    else:
        d = device
    session.add(d)
    session.commit()
    return {"status": "ok"}

@app.get("/log", response_model=List[Log])
def list_logs(session: Session = Depends(get_session)):
    return session.exec(select(Log)).all()
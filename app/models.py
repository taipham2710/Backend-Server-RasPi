from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    last_seen: datetime = Field(default_factory=datetime.utcnow)

class Log(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: int = Field(foreign_key="device.id")
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
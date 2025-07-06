from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=1)
    location: Optional[str] = Field(default=None)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    version: Optional[str] = Field(default=None, description="Current agent image version")
    status: Optional[str] = Field(default="offline", description="Agent status: online/offline")

class Log(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: int = Field(foreign_key="device.id")
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    log_level: Optional[str] = Field(default="info", description="Log level: info, warning, error, ...")
    type: Optional[str] = Field(default="general", description="Log type: general, deploy, rollback, ...")
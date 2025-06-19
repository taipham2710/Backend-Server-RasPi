from fastapi import APIRouter, Depends, HTTPException
from app.models import Log
from app.db import get_session
from app.crud import get_device_by_id, create_log, list_logs, get_log_by_id, update_log, delete_log, get_logs_by_device
from sqlmodel import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class LogCreate(BaseModel):
    device_id: int
    message: str
    timestamp: Optional[str] = None

class LogUpdate(BaseModel):
    message: Optional[str] = None
    timestamp: Optional[str] = None

@router.post("/log")
def receive_log(log: LogCreate, session: Session = Depends(get_session)):
    device = get_device_by_id(session, log.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Convert string timestamp to datetime if provided
    timestamp = datetime.utcnow()
    if log.timestamp:
        try:
            timestamp = datetime.fromisoformat(log.timestamp.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid timestamp format")
    
    # Create Log object
    log_obj = Log(
        device_id=log.device_id,
        message=log.message,
        timestamp=timestamp
    )
    
    create_log(session, log_obj)
    return {"status": "ok"}

@router.get("/log", response_model=List[Log])
def get_all_logs(session: Session = Depends(get_session)):
    return list_logs(session)

@router.get("/log/{log_id}", response_model=Log)
def get_log(log_id: int, session: Session = Depends(get_session)):
    log = get_log_by_id(session, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

@router.get("/device/{device_id}/logs", response_model=List[Log])
def get_device_logs(device_id: int, session: Session = Depends(get_session)):
    device = get_device_by_id(session, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return get_logs_by_device(session, device_id)

@router.put("/log/{log_id}", response_model=Log)
def update_log_endpoint(log_id: int, log_update: LogUpdate, session: Session = Depends(get_session)):
    log = update_log(session, log_id, log_update.dict(exclude_unset=True))
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

@router.delete("/log/{log_id}")
def delete_log_endpoint(log_id: int, session: Session = Depends(get_session)):
    success = delete_log(session, log_id)
    if not success:
        raise HTTPException(status_code=404, detail="Log not found")
    return {"message": "Log deleted successfully"}
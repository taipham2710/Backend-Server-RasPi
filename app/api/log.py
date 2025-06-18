from fastapi import APIRouter, Depends, HTTPException
from app.models import Log
from app.db import get_session
from app.crud import get_device_by_id, create_log, list_logs
from sqlmodel import Session
from typing import List

router = APIRouter()

@router.post("/log")
def receive_log(log: Log, session: Session = Depends(get_session)):
    device = get_device_by_id(session, log.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    create_log(session, log)
    return {"status": "ok"}

@router.get("/log", response_model=List[Log])
def get_all_logs(session: Session = Depends(get_session)):
    return list_logs(session)
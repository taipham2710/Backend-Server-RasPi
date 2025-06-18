from fastapi import APIRouter, Depends, HTTPException
from app.models import Device
from app.db import get_session
from app.crud import get_device_by_name, create_device, update_device_last_seen, list_devices
from sqlmodel import Session
from typing import List

router = APIRouter()

@router.get("/devices", response_model=List[Device])
def get_all_devices(session: Session = Depends(get_session)):
    return list_devices(session)

@router.post("/device/heartbeat")
def heartbeat(device: Device, session: Session = Depends(get_session)):
    d = get_device_by_name(session, device.name)
    if d:
        update_device_last_seen(session, d)
    else:
        create_device(session, device)
    return {"status": "ok"}
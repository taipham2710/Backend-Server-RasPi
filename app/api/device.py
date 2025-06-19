from fastapi import APIRouter, Depends, HTTPException
from app.models import Device
from app.db import get_session
from app.crud import get_device_by_name, create_device, update_device_last_seen, list_devices, get_device_by_id, update_device, delete_device
from sqlmodel import Session
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    last_seen: Optional[str] = None

class DeviceHeartbeat(BaseModel):
    name: str
    last_seen: Optional[str] = None

@router.get("/devices", response_model=List[Device])
def get_all_devices(session: Session = Depends(get_session)):
    return list_devices(session)

@router.get("/device/{device_id}", response_model=Device)
def get_device(device_id: int, session: Session = Depends(get_session)):
    device = get_device_by_id(session, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.post("/device/heartbeat")
def heartbeat(device: DeviceHeartbeat, session: Session = Depends(get_session)):
    if not device.name or device.name.strip() == "":
        raise HTTPException(status_code=400, detail="Device name is required")
    
    # Tạo Device object từ DeviceHeartbeat
    device_obj = Device(name=device.name.strip())
    
    d = get_device_by_name(session, device_obj.name)
    if d:
        update_device_last_seen(session, d)
    else:
        create_device(session, device_obj)
    return {"status": "ok"}

@router.put("/device/{device_id}", response_model=Device)
def update_device_endpoint(device_id: int, device_update: DeviceUpdate, session: Session = Depends(get_session)):
    device = update_device(session, device_id, device_update.dict(exclude_unset=True))
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.delete("/device/{device_id}")
def delete_device_endpoint(device_id: int, session: Session = Depends(get_session)):
    success = delete_device(session, device_id)
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"message": "Device deleted successfully"}
from fastapi import APIRouter, Depends, HTTPException
from app.models import Device
from app.db import get_session
from app.crud import get_device_by_name, create_device, update_device_last_seen, list_devices, get_device_by_id, update_device, delete_device
from sqlmodel import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from paho.mqtt import client as mqtt
import os
import pytz

router = APIRouter()

VN_TZ = pytz.timezone("Asia/Ho_Chi_Minh")

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    last_seen: Optional[str] = None

class DeviceHeartbeat(BaseModel):
    name: str
    version: Optional[str] = None
    status: Optional[str] = "online"
    location: Optional[str] = None

class DeviceResponse(BaseModel):
    id: int
    name: str
    version: Optional[str] = None
    status: Optional[str] = None
    last_seen: Optional[str] = None
    location: Optional[str] = None

    class Config:
        orm_mode = True

@router.get("/devices", response_model=List[DeviceResponse])
def get_all_devices(session: Session = Depends(get_session)):
    devices = list_devices(session)
    response = []
    for d in devices:
        if d.id is None:
            raise HTTPException(status_code=500, detail="Device id is None (database integrity error)")
        if d.last_seen:
            last_seen_vn = d.last_seen.astimezone(VN_TZ)
            last_seen = last_seen_vn.isoformat()
        else:
            last_seen = None
        response.append(DeviceResponse(
            id=d.id,
            name=d.name,
            version=d.version,
            status=d.status,
            last_seen=last_seen,
            location=d.location
        ))
    return response

@router.get("/device/{device_id}", response_model=DeviceResponse)
def get_device(device_id: int, session: Session = Depends(get_session)):
    device = get_device_by_id(session, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.id is None:
        raise HTTPException(status_code=500, detail="Device id is None (database integrity error)")
    if device.last_seen:
        last_seen_vn = device.last_seen.astimezone(VN_TZ)
        last_seen = last_seen_vn.isoformat()
    else:
        last_seen = None
    return DeviceResponse(
        id=device.id,
        name=device.name,
        version=device.version,
        status=device.status,
        last_seen=last_seen,
        location=device.location
    )

@router.get("/device/{device_id}/updates")
def check_device_updates(device_id: int, session: Session = Depends(get_session)):
    """Check for available updates for a specific device"""
    device = get_device_by_id(session, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # For now, return a mock response indicating no updates
    # In a real implementation, this would check for actual updates
    return {
        "device_id": device_id,
        "update_available": False,
        "current_version": "1.0.0",
        "latest_version": "1.0.0",
        "message": "No updates available"
    }

@router.post("/device/heartbeat")
def device_heartbeat(heartbeat: DeviceHeartbeat, session: Session = Depends(get_session)):
    now = datetime.utcnow()
    device = get_device_by_name(session, heartbeat.name)
    if not device:
        # If device is not found, create a new one
        device = Device(
            name=heartbeat.name,
            version=heartbeat.version,
            status=heartbeat.status or "online",
            last_seen=now,
            location=heartbeat.location
        )
        create_device(session, device)
    else:
        # Update existing device
        device.version = heartbeat.version
        device.status = heartbeat.status or "online"
        if heartbeat.location:
            device.location = heartbeat.location
        # Use update_device_last_seen to update last_seen
        update_device_last_seen(session, device)
        session.add(device)
        session.commit()
        session.refresh(device)
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

# Send update command to device via MQTT
# (topic follow type agent/{device_id}/cmd)
def send_update_command(device_id: int):
    broker = os.getenv("MQTT_BROKER", "localhost")
    port = int(os.getenv("MQTT_PORT", 1883))
    topic = f"agent/{device_id}/cmd"
    client = mqtt.Client()
    client.connect(broker, port, 60)
    client.loop_start()
    client.publish(topic, payload="update")
    client.loop_stop()
    client.disconnect()

@router.post("/device/{device_id}/update")
def trigger_update(device_id: int, session: Session = Depends(get_session)):
    device = get_device_by_id(session, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    try:
        send_update_command(device_id)
        return {"status": "update command sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send update command: {e}")
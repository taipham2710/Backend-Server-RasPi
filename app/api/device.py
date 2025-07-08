from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.models import Device
from app.db import get_session
from app.crud import get_device_by_name, create_device, update_device_last_seen, list_devices, get_device_by_id, update_device, delete_device
from sqlmodel import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timezone
from paho.mqtt import client as mqtt
import os
import pytz
import threading
import time
import requests
import re

router = APIRouter()

VN_TZ = pytz.timezone("Asia/Ho_Chi_Minh")

# Background task to set devices offline if no heartbeat
CHECK_INTERVAL = 30  # seconds
OFFLINE_THRESHOLD = 60  # seconds

# Background task: Notify Slack if new agent image version is available
LATEST_AGENT_VERSION = None
CHECK_IMAGE_INTERVAL = 300  # 5 phút

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

class DeviceCreate(BaseModel):
    id: int
    name: str
    version: Optional[str] = None
    status: Optional[str] = "online"
    location: Optional[str] = None

@router.get("/devices", response_model=List[DeviceResponse])
def get_all_devices(session: Session = Depends(get_session)):
    devices = list_devices(session)
    response = []
    for d in devices:
        if d.id is None:
            raise HTTPException(status_code=500, detail="Device id is None (database integrity error)")
        if d.last_seen:
            if d.last_seen.tzinfo is None:
                last_seen_utc = d.last_seen.replace(tzinfo=timezone.utc)
            else:
                last_seen_utc = d.last_seen.astimezone(timezone.utc)
            last_seen_vn = last_seen_utc.astimezone(VN_TZ)
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
        if device.last_seen.tzinfo is None:
            last_seen_utc = device.last_seen.replace(tzinfo=timezone.utc)
        else:
            last_seen_utc = device.last_seen.astimezone(timezone.utc)
        last_seen_vn = last_seen_utc.astimezone(VN_TZ)
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
    # Function to get the latest version from Docker Hub
    def get_latest_dockerhub_tag(DOCKERHUB_USERNAME, DOCKERHUB_REPO):
        url = f"https://hub.docker.com/v2/repositories/{DOCKERHUB_USERNAME}/{DOCKERHUB_REPO}/tags?page_size=100"
        try:
            resp = requests.get(url, timeout=5)
            tags = [t['name'] for t in resp.json().get('results', [])]
            tags = [t for t in tags if re.match(r'v\d+\.\d+', t)]
            tags.sort(key=lambda x: tuple(map(int, re.findall(r'\d+', x))), reverse=True)
            return tags[0] if tags else "v1.0"
        except Exception:
            return "v1.0"
    latest_version = get_latest_dockerhub_tag("taipham2710", "agent-raspi")
    device = get_device_by_id(session, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    current_version = device.version or "v1.0"
    update_available = (latest_version != current_version)
    return {
        "device_id": device_id,
        "update_available": update_available,
        "current_version": current_version,
        "latest_version": latest_version,
        "message": "Update available" if update_available else "No updates available"
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

@router.post("/device", response_model=DeviceResponse)
def create_device_endpoint(device: DeviceCreate, session: Session = Depends(get_session)):
    # Check if device with this id already exists
    existing = get_device_by_id(session, device.id)
    if existing:
        raise HTTPException(status_code=400, detail="Device with this id already exists")
    new_device = Device(
        id=device.id,
        name=device.name,
        version=device.version,
        status=device.status,
        location=device.location,
        last_seen=datetime.utcnow()
    )
    create_device(session, new_device)
    if new_device.id is None:
        raise HTTPException(status_code=500, detail="Device id is None (database integrity error)")
    return DeviceResponse(
        id=new_device.id,
        name=new_device.name,
        version=new_device.version,
        status=new_device.status,
        last_seen=new_device.last_seen.astimezone(VN_TZ).isoformat() if new_device.last_seen else None,
        location=new_device.location
    )

def offline_monitor_task():
    from app.db import get_session
    from datetime import datetime, timezone
    import pytz
    while True:
        session = next(get_session())
        devices = list_devices(session)
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        for d in devices:
            if d.last_seen:
                delta = (now - d.last_seen.replace(tzinfo=timezone.utc)).total_seconds()
                if delta > OFFLINE_THRESHOLD and d.status != "offline":
                    d.status = "offline"
                    session.add(d)
        session.commit()
        time.sleep(CHECK_INTERVAL)

# Start background thread when module loads
threading.Thread(target=offline_monitor_task, daemon=True).start()

def notify_new_agent_version():
    global LATEST_AGENT_VERSION
    DOCKERHUB_USERNAME = "taipham2710"
    DOCKERHUB_REPO = "agent-raspi"
    def get_latest_dockerhub_tag():
        url = f"https://hub.docker.com/v2/repositories/{DOCKERHUB_USERNAME}/{DOCKERHUB_REPO}/tags?page_size=100"
        try:
            resp = requests.get(url, timeout=5)
            tags = [t['name'] for t in resp.json().get('results', [])]
            tags = [t for t in tags if re.match(r'v\d+\.\d+', t)]
            tags.sort(key=lambda x: tuple(map(int, re.findall(r'\d+', x))), reverse=True)
            return tags[0] if tags else "v1.0"
        except Exception:
            return "v1.0"
    while True:
        latest_version = get_latest_dockerhub_tag()
        if LATEST_AGENT_VERSION is None:
            LATEST_AGENT_VERSION = latest_version
        elif latest_version != LATEST_AGENT_VERSION:
            # Send Slack notification
            blocks = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": f"🚀 New Agent Image Released!", "emoji": True}
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*A new agent image version is available on Docker Hub!*\n*Version:* `{latest_version}`"}
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"<https://hub.docker.com/r/{DOCKERHUB_USERNAME}/{DOCKERHUB_REPO}/tags|View on Docker Hub>"}
                }
            ]
            from app.api.log import send_slack_notification
            send_slack_notification("", channel="demo-events", blocks=blocks)
            LATEST_AGENT_VERSION = latest_version
        time.sleep(CHECK_IMAGE_INTERVAL)

# Start background thread for image version check
threading.Thread(target=notify_new_agent_version, daemon=True).start()
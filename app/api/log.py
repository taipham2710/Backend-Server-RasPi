from fastapi import APIRouter, Depends, HTTPException
from app.models import Log
from app.db import get_session
from app.crud import get_device_by_id, create_log, list_logs, get_log_by_id, update_log, delete_log, get_logs_by_device, get_latest_log_by_type
from sqlmodel import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from dateutil import parser
import os
import requests

router = APIRouter()

class LogCreate(BaseModel):
    device_id: int
    message: str
    log_level: Optional[str] = "info"
    type: Optional[str] = "general"
    timestamp: Optional[str] = None

class LogUpdate(BaseModel):
    message: Optional[str] = None
    timestamp: Optional[str] = None

def send_slack_notification(message: str, channel: str = "general", emoji: str = "🔔"):
    """Enhanced Slack notification with channel support and emoji"""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("SLACK_WEBHOOK_URL not set")
        return
    
    # Format message with emoji and channel
    formatted_message = f"{emoji} {message}"
    
    payload = {
        "text": formatted_message,
        "channel": channel if channel != "general" else None
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code != 200:
            print(f"Slack notification failed: {response.text}")
    except Exception as e:
        print(f"Slack notification error: {e}")

def send_demo_notification(event_type: str, device_name: str, details: str = ""):
    """Special notification for demo events"""
    emoji_map = {
        "deploy": "🚀",
        "rollback": "🔄", 
        "online": "✅",
        "offline": "❌",
        "update": "📦",
        "error": "🚨",
        "success": "🎉",
        "bulk_operation": "⚡"
    }
    
    emoji = emoji_map.get(event_type, "🔔")
    message = f"**Demo Event:** {event_type.upper()}\n**Device:** {device_name}\n**Details:** {details}"
    
    send_slack_notification(message, "demo-events", emoji)

@router.post("/logs")
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
        timestamp=timestamp,
        log_level=log.log_level,
        type=log.type
    )
    
    create_log(session, log_obj)
    
    # Enhanced Slack notifications for different log types
    if log.type in ("deploy", "rollback"):
        log_type = log.type.upper() if log.type else "UNKNOWN"
        log_level = log.log_level.upper() if log.log_level else "UNKNOWN"
        emoji = "🚀" if log.type == "deploy" else "🔄"
        slack_msg = f"[{log_type}][{log_level}] Device {device.name}: {log.message}"
        send_slack_notification(slack_msg, "iot-deployments", emoji)
        
        # Send demo notification
        send_demo_notification(log.type, device.name, log.message)
    
    elif log.type == "system":
        # System monitoring logs
        emoji = "💻"
        slack_msg = f"[SYSTEM] Device {device.name}: {log.message}"
        send_slack_notification(slack_msg, "iot-monitoring", emoji)
    
    elif log.log_level == "error":
        # Error logs
        emoji = "🚨"
        slack_msg = f"[ERROR] Device {device.name}: {log.message}"
        send_slack_notification(slack_msg, "iot-alerts", emoji)
    
    elif log.type == "heartbeat":
        # Heartbeat logs (only for demo)
        if "offline" in log.message.lower():
            emoji = "❌"
            slack_msg = f"[OFFLINE] Device {device.name} is offline"
            send_slack_notification(slack_msg, "iot-status", emoji)
            send_demo_notification("offline", device.name, "Device went offline")
        elif "online" in log.message.lower():
            emoji = "✅"
            slack_msg = f"[ONLINE] Device {device.name} is back online"
            send_slack_notification(slack_msg, "iot-status", emoji)
            send_demo_notification("online", device.name, "Device came back online")
    
    return {"status": "ok"}

@router.get("/logs", response_model=List[Log])
def get_all_logs(session: Session = Depends(get_session)):
    return list_logs(session)

@router.get("/logs/{log_id}", response_model=Log)
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
    
@router.put("/logs/{log_id}", response_model=Log)
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

@router.get("/device/{device_id}/latest-log")
def get_device_latest_log(device_id: int, type: str, session: Session = Depends(get_session)):
    device = get_device_by_id(session, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    log = get_latest_log_by_type(session, device_id, type)
    if not log:
        raise HTTPException(status_code=404, detail="No log found for this type")
    # Đảm bảo timestamp là datetime object (nếu là string thì convert)
    if isinstance(log.timestamp, str):
        log.timestamp = parser.isoparse(log.timestamp)
    return log.dict()

# Demo-specific endpoints for bulk operations
@router.post("/demo/bulk-update")
def demo_bulk_update(session: Session = Depends(get_session)):
    """Demo endpoint for bulk update simulation"""
    from app.crud import list_devices
    
    devices = list_devices(session)
    device_count = len(devices)
    
    # Send demo notification
    send_demo_notification(
        "bulk_operation", 
        f"{device_count} devices", 
        f"Bulk update initiated for {device_count} devices"
    )
    
    # Send to specific channels
    send_slack_notification(
        f"🚀 **BULK UPDATE DEMO**\nInitiating update for {device_count} devices",
        "demo-events"
    )
    
    return {
        "message": f"Bulk update demo initiated for {device_count} devices",
        "device_count": device_count,
        "status": "demo_mode"
    }

@router.post("/demo/system-failure")
def demo_system_failure(session: Session = Depends(get_session)):
    """Demo endpoint for system failure simulation"""
    from app.crud import list_devices
    import random
    
    devices = list_devices(session)
    if not devices:
        raise HTTPException(status_code=404, detail="No devices found")
    
    # Simulate random device failure
    failed_device = random.choice(devices)
    
    # Send demo notifications
    send_demo_notification(
        "error", 
        failed_device.name, 
        "Simulated system failure for demo"
    )
    
    send_slack_notification(
        f"🚨 **DEMO: System Failure**\nDevice {failed_device.name} simulated failure",
        "demo-events"
    )
    
    return {
        "message": f"System failure demo: {failed_device.name}",
        "failed_device": failed_device.name,
        "status": "demo_mode"
    }
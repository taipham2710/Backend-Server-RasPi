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
import json

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

def send_slack_notification(message: str, channel: str = "general", emoji: str = "🔔", blocks: Optional[list] = None):
    """Enhanced Slack notification with channel support, emoji, and Block Kit"""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("SLACK_WEBHOOK_URL not set")
        return
    
    if blocks:
        payload = {
            "blocks": blocks,
            "channel": channel if channel != "general" else None
        }
    else:
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

def send_demo_notification(event_type: str, device_name: str, details: str = "", version: Optional[str] = None):
    """Special notification for demo events with Block Kit"""
    emoji_map = {
        "deploy": ":rocket:",
        "rollback": ":arrows_counterclockwise:",
        "online": ":white_check_mark:",
        "offline": ":x:",
        "update": ":package:",
        "error": ":rotating_light:",
        "success": ":tada:",
        "bulk_operation": ":zap:"
    }
    color_map = {
        "deploy": "#36a64f",
        "rollback": "#e6c229",
        "online": "#2eb67d",
        "offline": "#e01e5a",
        "update": "#439fe0",
        "error": "#e01e5a",
        "success": "#36a64f",
        "bulk_operation": "#439fe0"
    }
    emoji = emoji_map.get(event_type, ":bell:")
    color = color_map.get(event_type, "#439fe0")
    title = event_type.replace("_", " ").title()
    # Gộp các trường vào 1 block mrkdwn, dùng *bold* đúng chuẩn Slack
    text = f"*Device:* {device_name}\n"
    if version:
        text += f"*Version:* {version}\n"
    text += f"*Details:* {details}"
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"{emoji} {title} Event", "emoji": True}
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": text}
        }
    ]
    send_slack_notification("", channel="demo-events", blocks=blocks)

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
        # Block Kit cho event này, dùng *bold* đúng chuẩn Slack
        text = f"*Device:* {device.name}\n*Level:* {log_level}\n*Details:* {log.message}"
        send_slack_notification(
            "",
            channel="iot-deployments",
            blocks=[
                {"type": "header", "text": {"type": "plain_text", "text": f"{emoji} {log_type} Event", "emoji": True}},
                {"type": "section", "text": {"type": "mrkdwn", "text": text}}
            ]
        )
        send_demo_notification(log.type, device.name, log.message)
    elif log.type == "system":
        emoji = "💻"
        slack_msg = f"[SYSTEM] Device {device.name}: {log.message}"
        send_slack_notification(slack_msg, "iot-monitoring", emoji)
    elif log.log_level == "error":
        emoji = "🚨"
        text = f"*Device:* {device.name}\n*Details:* {log.message}"
        send_slack_notification(
            "",
            channel="iot-alerts",
            blocks=[
                {"type": "header", "text": {"type": "plain_text", "text": f"{emoji} ERROR", "emoji": True}},
                {"type": "section", "text": {"type": "mrkdwn", "text": text}}
            ]
        )
    elif log.type == "heartbeat":
        if "offline" in log.message.lower():
            emoji = "❌"
            text = f"*Device:* {device.name}\n*Details:* Device went offline"
            send_slack_notification(
                "",
                channel="iot-status",
                blocks=[
                    {"type": "header", "text": {"type": "plain_text", "text": f"{emoji} OFFLINE", "emoji": True}},
                    {"type": "section", "text": {"type": "mrkdwn", "text": text}}
                ]
            )
            send_demo_notification("offline", device.name, "Device went offline")
        elif "online" in log.message.lower():
            emoji = "✅"
            text = f"*Device:* {device.name}\n*Details:* Device came back online"
            send_slack_notification(
                "",
                channel="iot-status",
                blocks=[
                    {"type": "header", "text": {"type": "plain_text", "text": f"{emoji} ONLINE", "emoji": True}},
                    {"type": "section", "text": {"type": "mrkdwn", "text": text}}
                ]
            )
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
    
    # Send demo notification (Block Kit)
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "🚀 BULK UPDATE DEMO", "emoji": True}
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"Initiating update for {device_count} devices"}
        }
    ]
    send_slack_notification("", "demo-events", blocks=blocks)
    
    # Send to specific channels (Block Kit)
    blocks2 = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "⚡ BULK OPERATION", "emoji": True}
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Devices:* {device_count}\n*Details:* Bulk update initiated for {device_count} devices"}
        }
    ]
    send_slack_notification("", "demo-events", blocks=blocks2)
    
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
    
    # Send demo notifications (Block Kit)
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "🔔 :rotating_light: DEMO: System Failure", "emoji": True}
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"Device {failed_device.name} simulated failure"}
        }
    ]
    send_slack_notification("", "demo-events", blocks=blocks)
    
    return {
        "message": f"System failure demo: {failed_device.name}",
        "failed_device": failed_device.name,
        "status": "demo_mode"
    }
from sqlmodel import select
from app.models import Device, Log

def get_device_by_id(session, device_id: int):
    return session.get(Device, device_id)

def get_device_by_name(session, name: str):
    return session.exec(select(Device).where(Device.name == name)).first()

def create_device(session, device: Device):
    session.add(device)
    session.commit()
    session.refresh(device)
    return device

def update_device_last_seen(session, device: Device):
    from datetime import datetime
    device.last_seen = datetime.utcnow()
    session.add(device)
    session.commit()
    session.refresh(device)
    return device

def create_log(session, log: Log):
    session.add(log)
    session.commit()
    session.refresh(log)
    return log

def list_devices(session):
    from sqlmodel import select
    return session.exec(select(Device)).all()

def list_logs(session):
    from sqlmodel import select
    return session.exec(select(Log)).all()
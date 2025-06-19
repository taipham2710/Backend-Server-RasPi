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

def update_device(session, device_id: int, device_data: dict):
    device = session.get(Device, device_id)
    if not device:
        return None
    
    for key, value in device_data.items():
        if hasattr(device, key):
            setattr(device, key, value)
    
    session.add(device)
    session.commit()
    session.refresh(device)
    return device

def delete_device(session, device_id: int):
    device = session.get(Device, device_id)
    if not device:
        return False
    
    session.delete(device)
    session.commit()
    return True

def create_log(session, log: Log):
    session.add(log)
    session.commit()
    session.refresh(log)
    return log

def get_log_by_id(session, log_id: int):
    return session.get(Log, log_id)

def update_log(session, log_id: int, log_data: dict):
    log = session.get(Log, log_id)
    if not log:
        return None
    
    for key, value in log_data.items():
        if hasattr(log, key):
            setattr(log, key, value)
    
    session.add(log)
    session.commit()
    session.refresh(log)
    return log

def delete_log(session, log_id: int):
    log = session.get(Log, log_id)
    if not log:
        return False
    
    session.delete(log)
    session.commit()
    return True

def list_devices(session):
    from sqlmodel import select
    return session.exec(select(Device)).all()

def list_logs(session):
    from sqlmodel import select
    return session.exec(select(Log)).all()

def get_logs_by_device(session, device_id: int):
    return session.exec(select(Log).where(Log.device_id == device_id)).all()
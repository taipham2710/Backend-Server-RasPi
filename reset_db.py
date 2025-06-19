#!/usr/bin/env python3
"""
Script để reset database và tạo lại schema
"""
import os
from sqlmodel import SQLModel
from app.db import engine

def reset_database():
    """Xóa database cũ và tạo lại schema"""
    # Xóa file database cũ nếu tồn tại
    if os.path.exists("iot.db"):
        os.remove("iot.db")
        print("Đã xóa database cũ: iot.db")
    
    # Tạo database và schema mới
    SQLModel.metadata.create_all(engine)
    print("Đã tạo database mới với schema cập nhật: iot.db")

if __name__ == "__main__":
    reset_database() 
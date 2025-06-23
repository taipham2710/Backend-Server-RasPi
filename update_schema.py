#!/usr/bin/env python3
"""
Script để cập nhật schema database mà không mất dữ liệu
"""
from sqlmodel import SQLModel
from app.models import Device, Log
from app.db import engine

def update_database():
    # This will add the new 'location' column to existing devices table
    SQLModel.metadata.create_all(engine)
    print("Database schema updated successfully!")

if __name__ == "__main__":
    update_database() 
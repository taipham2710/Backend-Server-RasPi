#!/usr/bin/env python3
"""
Script để cập nhật schema database mà không mất dữ liệu
"""
from sqlmodel import SQLModel
from app.db import engine

def update_schema():
    """Cập nhật schema database"""
    try:
        # Tạo các bảng mới nếu chưa tồn tại
        SQLModel.metadata.create_all(engine)
        print("Đã cập nhật schema database thành công!")
        print("Lưu ý: Nếu có thay đổi trong cấu trúc bảng, có thể cần backup dữ liệu trước")
    except Exception as e:
        print(f"Lỗi khi cập nhật schema: {e}")
        print("Nếu gặp lỗi, hãy backup dữ liệu và chạy reset_db.py")

if __name__ == "__main__":
    update_schema() 
# IoT Device Backend API

Backend API cho quản lý thiết bị IoT và logs sử dụng FastAPI và SQLModel.

## Tính năng

- **Device Management**: Tạo, đọc, cập nhật, xóa thiết bị
- **Log Management**: Tạo, đọc, cập nhật, xóa logs
- **Heartbeat System**: Hệ thống heartbeat cho thiết bị
- **RESTful API**: API đầy đủ với validation

## Cài đặt

1. **Clone repository**:
```bash
git clone <repository-url>
cd Backend-RasPi
```

2. **Tạo virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

3. **Cài đặt dependencies**:
```bash
pip install -r requirements.txt
```

4. **Khởi tạo database**:
```bash
python3 update_schema.py
```

## Chạy ứng dụng

### Development mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production mode với Docker
```bash
docker build -t iot-backend .
docker run -p 8000:8000 iot-backend
```

## API Documentation

Sau khi chạy server, truy cập:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Chi tiết API endpoints xem file `API_DOCUMENTATION.md`

## Testing

Chạy test script để kiểm tra API:
```bash
python3 test_api.py
```

## Database

- **File**: `iot.db` (SQLite)
- **Reset database**: `python3 reset_db.py`
- **Update schema**: `python3 update_schema.py`

## Cấu trúc Project

```
Backend-RasPi/
├── app/
│   ├── api/
│   │   ├── device.py      # Device endpoints
│   │   └── log.py         # Log endpoints
│   ├── crud.py            # Database operations
│   ├── db.py              # Database configuration
│   ├── main.py            # FastAPI app
│   └── models.py          # SQLModel models
├── API_DOCUMENTATION.md   # API documentation
├── test_api.py           # Test script
├── update_schema.py      # Schema update script
├── reset_db.py           # Database reset script
├── requirements.txt      # Python dependencies
└── Dockerfile           # Docker configuration
```

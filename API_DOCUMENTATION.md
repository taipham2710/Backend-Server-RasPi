# API Documentation - IoT Device Backend

## Device Endpoints

### 1. Lấy tất cả devices
```
GET /devices
```
**Response:** Danh sách tất cả devices

### 2. Lấy device theo ID
```
GET /device/{device_id}
```
**Response:** Thông tin device cụ thể

### 3. Tạo hoặc cập nhật device heartbeat
```
POST /device/heartbeat
```
**Body:**
```json
{
  "name": "device_name",
  "last_seen": "2024-01-01T12:00:00"
}
```
**Lưu ý:** Trường `name` là bắt buộc, `last_seen` là tùy chọn

### 4. Cập nhật device
```
PUT /device/{device_id}
```
**Body:**
```json
{
  "name": "new_device_name",
  "last_seen": "2024-01-01T12:00:00"
}
```
**Lưu ý:** Chỉ cần gửi các trường muốn cập nhật

### 5. Xóa device
```
DELETE /device/{device_id}
```
**Response:** 
```json
{
  "message": "Device deleted successfully"
}
```

## Log Endpoints

### 1. Tạo log mới
```
POST /log
```
**Body:**
```json
{
  "device_id": 1,
  "message": "Log message",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 2. Lấy tất cả logs
```
GET /log
```
**Response:** Danh sách tất cả logs

### 3. Lấy log theo ID
```
GET /log/{log_id}
```
**Response:** Thông tin log cụ thể

### 4. Lấy logs theo device
```
GET /device/{device_id}/logs
```
**Response:** Danh sách logs của device cụ thể

### 5. Cập nhật log
```
PUT /log/{log_id}
```
**Body:**
```json
{
  "message": "Updated log message",
  "timestamp": "2024-01-01T12:00:00"
}
```
**Lưu ý:** Chỉ cần gửi các trường muốn cập nhật

### 6. Xóa log
```
DELETE /log/{log_id}
```
**Response:**
```json
{
  "message": "Log deleted successfully"
}
```

## Error Responses

### 404 Not Found
```json
{
  "detail": "Device not found"
}
```
hoặc
```json
{
  "detail": "Log not found"
}
```

### 400 Bad Request
```json
{
  "detail": "Device name is required"
}
```

## Ví dụ sử dụng với curl

### Tạo device heartbeat
```bash
curl -X POST "http://localhost:8000/device/heartbeat" \
  -H "Content-Type: application/json" \
  -d '{"name": "raspberry_pi_01"}'
```

### Cập nhật device
```bash
curl -X PUT "http://localhost:8000/device/1" \
  -H "Content-Type: application/json" \
  -d '{"name": "updated_device_name"}'
```

### Xóa device
```bash
curl -X DELETE "http://localhost:8000/device/1"
```

### Cập nhật log
```bash
curl -X PUT "http://localhost:8000/log/1" \
  -H "Content-Type: application/json" \
  -d '{"message": "Updated log message"}'
```

### Xóa log
```bash
curl -X DELETE "http://localhost:8000/log/1"
```

### Lấy logs của device cụ thể
```bash
curl -X GET "http://localhost:8000/device/1/logs"
``` 
#!/usr/bin/env python3
"""
Script test để kiểm tra các API endpoints
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://taipham2710.sytes.net:8000"

def test_device_endpoints():
    """Test các endpoints liên quan đến Device"""
    print("=== Testing Device Endpoints ===")
    
    # Test 1: Tạo device heartbeat
    print("\n1. Testing device heartbeat...")
    heartbeat_data = {
        "name": "test_device_01",
        "last_seen": datetime.utcnow().isoformat()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/device/heartbeat", json=heartbeat_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Lấy tất cả devices
    print("\n2. Testing get all devices...")
    devices = []
    try:
        response = requests.get(f"{BASE_URL}/devices")
        print(f"Status: {response.status_code}")
        devices = response.json()
        print(f"Found {len(devices)} devices")
        for device in devices:
            print(f"  - ID: {device['id']}, Name: {device['name']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Lấy device theo ID (nếu có)
    if devices:
        device_id = devices[0]['id']
        print(f"\n3. Testing get device by ID ({device_id})...")
        try:
            response = requests.get(f"{BASE_URL}/device/{device_id}")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 4: Cập nhật device
        print(f"\n4. Testing update device ({device_id})...")
        update_data = {
            "name": "updated_test_device"
        }
        try:
            response = requests.put(f"{BASE_URL}/device/{device_id}", json=update_data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")

def test_log_endpoints():
    """Test các endpoints liên quan đến Log"""
    print("\n=== Testing Log Endpoints ===")
    
    # Test 1: Tạo log
    print("\n1. Testing create log...")
    log_data = {
        "device_id": 1,  # Giả sử device ID 1 tồn tại
        "message": "Test log message",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/log", json=log_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Lấy tất cả logs
    print("\n2. Testing get all logs...")
    try:
        response = requests.get(f"{BASE_URL}/log")
        print(f"Status: {response.status_code}")
        logs = response.json()
        print(f"Found {len(logs)} logs")
        for log in logs:
            print(f"  - ID: {log['id']}, Device: {log['device_id']}, Message: {log['message']}")
    except Exception as e:
        print(f"Error: {e}")

def test_error_cases():
    """Test các trường hợp lỗi"""
    print("\n=== Testing Error Cases ===")
    
    # Test 1: Heartbeat không có name
    print("\n1. Testing heartbeat without name...")
    try:
        response = requests.post(f"{BASE_URL}/device/heartbeat", json={})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Lấy device không tồn tại
    print("\n2. Testing get non-existent device...")
    try:
        response = requests.get(f"{BASE_URL}/device/999")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Starting API tests...")
    print("Make sure the server is running on http://localhost:8000")
    
    try:
        test_device_endpoints()
        test_log_endpoints()
        test_error_cases()
        print("\n=== All tests completed ===")
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}") 
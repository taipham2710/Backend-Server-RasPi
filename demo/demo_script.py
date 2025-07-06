#!/usr/bin/env python3
"""
Demo Script for IoT Device Management System
This script simulates various scenarios for presentation purposes
"""

import requests
import time
import random
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DemoController:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def send_log(self, device_id: int, message: str, log_type: str = "general", log_level: str = "info"):
        """Send a log message to the backend"""
        url = f"{self.base_url}/api/logs"
        data = {
            "device_id": device_id,
            "message": message,
            "log_level": log_level,
            "type": log_type
        }
        
        try:
            response = self.session.post(url, json=data)
            if response.status_code == 200:
                print(f"✅ Log sent: {message}")
                return True
            else:
                print(f"❌ Failed to send log: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error sending log: {e}")
            return False
    
    def get_devices(self):
        """Get all devices"""
        url = f"{self.base_url}/api/devices"
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get devices: {response.text}")
                return []
        except Exception as e:
            print(f"❌ Error getting devices: {e}")
            return []
    
    def trigger_bulk_update(self):
        """Trigger bulk update demo"""
        url = f"{self.base_url}/api/demo/bulk-update"
        try:
            response = self.session.post(url)
            if response.status_code == 200:
                result = response.json()
                print(f"🚀 Bulk update demo triggered: {result['message']}")
                return True
            else:
                print(f"❌ Failed to trigger bulk update: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error triggering bulk update: {e}")
            return False
    
    def trigger_system_failure(self):
        """Trigger system failure demo"""
        url = f"{self.base_url}/api/demo/system-failure"
        try:
            response = self.session.post(url)
            if response.status_code == 200:
                result = response.json()
                print(f"🚨 System failure demo triggered: {result['message']}")
                return True
            else:
                print(f"❌ Failed to trigger system failure: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error triggering system failure: {e}")
            return False

def demo_scenario_1_basic_operation():
    """Demo Scenario 1: Basic IoT Operations"""
    print("\n" + "="*60)
    print("🎯 DEMO SCENARIO 1: Basic IoT Operations")
    print("="*60)
    
    controller = DemoController()
    
    # Simulate device heartbeats
    print("\n📡 Simulating device heartbeats...")
    for i in range(1, 6):
        controller.send_log(
            device_id=i,
            message=f"Device {i} heartbeat - CPU: {random.randint(10, 80)}%, Memory: {random.randint(20, 90)}%",
            log_type="heartbeat",
            log_level="info"
        )
        time.sleep(1)
    
    # Simulate system monitoring
    print("\n💻 Simulating system monitoring...")
    for i in range(1, 4):
        controller.send_log(
            device_id=i,
            message=f"System health check - Disk: {random.randint(30, 95)}% used, Network: {random.randint(1, 100)} Mbps",
            log_type="system",
            log_level="info"
        )
        time.sleep(0.5)

def demo_scenario_2_deployment_operations():
    """Demo Scenario 2: Deployment Operations"""
    print("\n" + "="*60)
    print("🚀 DEMO SCENARIO 2: Deployment Operations")
    print("="*60)
    
    controller = DemoController()
    
    # Simulate deployment process
    print("\n📦 Simulating deployment process...")
    for i in range(1, 4):
        # Start deployment
        controller.send_log(
            device_id=i,
            message=f"Starting deployment of version 2.1.0",
            log_type="deploy",
            log_level="info"
        )
        time.sleep(1)
        
        # Deployment success
        controller.send_log(
            device_id=i,
            message=f"Deployment completed successfully - version 2.1.0 active",
            log_type="deploy",
            log_level="info"
        )
        time.sleep(1)
    
    # Simulate one failed deployment
    print("\n⚠️ Simulating failed deployment...")
    controller.send_log(
        device_id=4,
        message=f"Deployment failed - insufficient disk space",
        log_type="deploy",
        log_level="error"
    )
    time.sleep(1)
    
    # Simulate rollback
    print("\n🔄 Simulating rollback...")
    controller.send_log(
        device_id=4,
        message=f"Rolling back to previous version 2.0.5",
        log_type="rollback",
        log_level="warning"
    )
    time.sleep(1)
    
    controller.send_log(
        device_id=4,
        message=f"Rollback completed successfully",
        log_type="rollback",
        log_level="info"
    )

def demo_scenario_3_bulk_operations():
    """Demo Scenario 3: Bulk Operations"""
    print("\n" + "="*60)
    print("⚡ DEMO SCENARIO 3: Bulk Operations")
    print("="*60)
    
    controller = DemoController()
    
    # Trigger bulk update
    print("\n🚀 Triggering bulk update for all devices...")
    controller.trigger_bulk_update()
    time.sleep(2)
    
    # Simulate bulk deployment
    print("\n📦 Simulating bulk deployment...")
    for i in range(1, 6):
        controller.send_log(
            device_id=i,
            message=f"Bulk deployment initiated - updating to version 2.2.0",
            log_type="deploy",
            log_level="info"
        )
        time.sleep(0.3)
    
    # Simulate bulk success
    print("\n✅ Simulating bulk deployment success...")
    for i in range(1, 6):
        controller.send_log(
            device_id=i,
            message=f"Bulk deployment completed - version 2.2.0 active",
            log_type="deploy",
            log_level="info"
        )
        time.sleep(0.3)

def demo_scenario_4_failure_recovery():
    """Demo Scenario 4: Failure and Recovery"""
    print("\n" + "="*60)
    print("🚨 DEMO SCENARIO 4: Failure and Recovery")
    print("="*60)
    
    controller = DemoController()
    
    # Trigger system failure
    print("\n🚨 Triggering system failure simulation...")
    controller.trigger_system_failure()
    time.sleep(2)
    
    # Simulate device going offline
    print("\n❌ Simulating device going offline...")
    controller.send_log(
        device_id=3,
        message=f"Device connection lost - network timeout",
        log_type="heartbeat",
        log_level="error"
    )
    time.sleep(2)
    
    # Simulate device coming back online
    print("\n✅ Simulating device recovery...")
    controller.send_log(
        device_id=3,
        message=f"Device connection restored - back online",
        log_type="heartbeat",
        log_level="info"
    )
    time.sleep(1)
    
    # Simulate error recovery
    print("\n🔄 Simulating error recovery...")
    controller.send_log(
        device_id=3,
        message=f"System recovery completed - all services restored",
        log_type="system",
        log_level="info"
    )

def demo_scenario_5_real_time_monitoring():
    """Demo Scenario 5: Real-time Monitoring"""
    print("\n" + "="*60)
    print("📊 DEMO SCENARIO 5: Real-time Monitoring")
    print("="*60)
    
    controller = DemoController()
    
    # Simulate continuous monitoring
    print("\n📡 Simulating real-time monitoring (10 seconds)...")
    start_time = time.time()
    
    while time.time() - start_time < 10:
        # Random device monitoring
        device_id = random.randint(1, 5)
        cpu_usage = random.randint(5, 95)
        memory_usage = random.randint(10, 90)
        
        controller.send_log(
            device_id=device_id,
            message=f"Real-time monitoring - CPU: {cpu_usage}%, Memory: {memory_usage}%",
            log_type="system",
            log_level="info"
        )
        
        time.sleep(2)
    
    print("\n✅ Real-time monitoring simulation completed")

def run_full_demo():
    """Run the complete demo sequence"""
    print("🎬 STARTING IOT DEVICE MANAGEMENT SYSTEM DEMO")
    print("="*60)
    print("This demo will showcase:")
    print("1. Basic IoT Operations")
    print("2. Deployment Operations") 
    print("3. Bulk Operations")
    print("4. Failure and Recovery")
    print("5. Real-time Monitoring")
    print("="*60)
    
    input("\nPress Enter to start the demo...")
    
    try:
        demo_scenario_1_basic_operation()
        time.sleep(3)
        
        demo_scenario_2_deployment_operations()
        time.sleep(3)
        
        demo_scenario_3_bulk_operations()
        time.sleep(3)
        
        demo_scenario_4_failure_recovery()
        time.sleep(3)
        
        demo_scenario_5_real_time_monitoring()
        
        print("\n" + "="*60)
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("Check your Slack channels for notifications:")
        print("- #demo-events: Demo-specific events")
        print("- #iot-deployments: Deployment notifications")
        print("- #iot-monitoring: System monitoring")
        print("- #iot-alerts: Error alerts")
        print("- #iot-status: Device status changes")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")

def run_single_scenario(scenario_number: int):
    """Run a single demo scenario"""
    scenarios = {
        1: demo_scenario_1_basic_operation,
        2: demo_scenario_2_deployment_operations,
        3: demo_scenario_3_bulk_operations,
        4: demo_scenario_4_failure_recovery,
        5: demo_scenario_5_real_time_monitoring
    }
    
    if scenario_number in scenarios:
        scenarios[scenario_number]()
    else:
        print(f"❌ Invalid scenario number: {scenario_number}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        try:
            scenario = int(sys.argv[1])
            run_single_scenario(scenario)
        except ValueError:
            print("❌ Invalid scenario number. Use 1-5 or no arguments for full demo.")
    else:
        run_full_demo() 
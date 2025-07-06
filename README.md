# IoT Device Backend API

> **Python version management:**
>
> This project uses [pyenv](https://github.com/pyenv/pyenv) for Python version management. The required Python version is specified in the `.python-version` file (committed to the repo).
>
> **To set up the correct Python version:**
> 1. Install pyenv if you haven't:
>    ```bash
>    brew install pyenv openssl
>    ```
> 2. Install the required Python version:
>    ```bash
>    pyenv install $(cat .python-version)
>    ```
> 3. Set local version (usually auto by .python-version):
>    ```bash
>    pyenv local $(cat .python-version)
>    ```
> 4. (Recommended) Create a new virtual environment after switching Python version:
>    ```bash
>    python -m venv venv
>    source venv/bin/activate
>    ```
> 5. Continue with requirements installation as below.

Backend API for IoT device management and logs using FastAPI and SQLModel.

## Features

- **Device Management**: Create, read, update, delete devices
- **Log Management**: Create, read, update, delete logs
- **Heartbeat System**: Device heartbeat system
- **RESTful API**: Full-featured API with validation

## Demo

The project includes a demo script to simulate real-world IoT scenarios for presentations and testing. The demo is located in the `demo/` folder for better organization:

- **Location:** `demo/demo_script.py`

### What does the demo do?
The demo script simulates multiple IoT devices interacting with the backend, sending logs, triggering deployments, simulating failures, and more. It is designed to showcase the main features of the system and to help you test or present the platform.

### Demo Scenarios
The demo supports running all scenarios in sequence or a single scenario by number:

1. **Basic IoT Operations:**
   - Simulates device heartbeats and system monitoring logs.
2. **Deployment Operations:**
   - Simulates deployments, including both successful and failed deployments with rollback.
3. **Bulk Operations:**
   - Simulates bulk update and deployment across multiple devices.
4. **Failure and Recovery:**
   - Simulates system failure, device going offline, and recovery.
5. **Real-time Monitoring:**
   - Simulates real-time monitoring data from devices over a period of time.

### How to run the demo

**Run the full demo (all scenarios):**
```bash
python demo/demo_script.py
```

**Run a single scenario (replace N with 1-5):**
```bash
python demo/demo_script.py N
```

---

## Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd Backend-RasPi
```

2. **Create a virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Initialize the database**:
```bash
python3 update_schema.py
```

## Running the Application

### Development mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production mode with Docker
```bash
docker build -t iot-backend .
docker run -p 8000:8000 iot-backend
```

## API Documentation

After starting the server, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

See `API_DOCUMENTATION.md` for detailed API endpoints.

## Testing

Run the test script to verify the API:
```bash
python3 test_api.py
```

## Database

- **File**: `iot.db` (SQLite)
- **Reset database**: `python3 reset_db.py`
- **Update schema**: `python3 update_schema.py`

## Project Structure

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
├── demo/
│   └── demo_script.py     # Demo scenarios and simulation
├── API_DOCUMENTATION.md   # API documentation
├── test_api.py            # Test script
├── update_schema.py       # Schema update script
├── reset_db.py            # Database reset script
├── requirements.txt       # Python dependencies
└── Dockerfile             # Docker configuration
```

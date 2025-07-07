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

The demo script to simulate IoT scenarios is now located in the Agent-RasPi repository for better modularity and maintenance.

- **Location:** `Agent-RasPi/demo/demo_script.py`

### How to run the demo

**Run the full demo (all scenarios):**
```bash
cd ../Agent-RasPi/demo
python demo_script.py
```

**Run a single scenario (replace N with 1-5):**
```bash
cd ../Agent-RasPi/demo
python demo_script.py N
```

**You can set the backend URL via the BACKEND_URL environment variable:**
```bash
BACKEND_URL=http://your-backend-url:8000 python demo_script.py
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
├── API_DOCUMENTATION.md   # API documentation
├── test_api.py            # Test script
├── update_schema.py       # Schema update script
├── reset_db.py            # Database reset script
├── requirements.txt       # Python dependencies
└── Dockerfile             # Docker configuration
```

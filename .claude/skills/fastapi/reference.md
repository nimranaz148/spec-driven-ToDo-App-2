# FastAPI Reference Guide

## Table of Contents
1. [Advanced Routing](#advanced-routing)
2. [Middleware](#middleware)
3. [Testing](#testing)
4. [Performance](#performance)
5. [Deployment](#deployment)

---

## Advanced Routing

### Path Parameters
```python
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

### Enum Path Parameters
```python
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

@app.get("/tasks/{status}")
async def get_tasks_by_status(status: TaskStatus):
    return {"status": status}
```

### Request Body + Path + Query
```python
@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Item,
    q: str | None = Query(None, min_length=3)
):
    return {"item_id": item_id, **item.model_dump(), "q": q}
```

### File Uploads
```python
from fastapi import UploadFile, File

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename, "size": len(contents)}
```

---

## Middleware

### CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://myapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Custom Middleware
```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class TimerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        process = time.time() - start
        response.headers["X-Process-Time"] = str(process)
        return response

app.add_middleware(TimerMiddleware)
```

### Logging Middleware
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response
```

---

## Testing

### Using TestClient
```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_item():
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == {"item_id": 1, "q": None}

def test_create_item():
    response = client.post(
        "/items",
        json={"title": "Test", "description": "A test item"}
    )
    assert response.status_code == 200
    assert "id" in response.json()
```

### Testing with Dependencies
```python
from unittest.mock import patch

def test_create_task_with_mock_db():
    with patch("main.get_db") as mock_db:
        mock_db.return_value = MagicMock()
        response = client.post(
            "/api/user1/tasks",
            json={"title": "Test task"},
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code == 200
```

### Async Testing
```python
import pytest
from httpx import AsyncClient, ASGITransport

@pytest.mark.asyncio
async def test_async():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
```

---

## Performance

### Connection Pooling
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)
```

### Background Tasks
```python
from fastapi import BackgroundTasks

def write_log(message: str):
    with open("log.txt", "a") as f:
        f.write(message + "\n")

@app.post("/send-notification/")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_log, f"Notification sent to {email}")
    return {"message": "Notification queued"}
```

### Streaming Responses
```python
from fastapi.responses import StreamingResponse
import time

def generate():
    for i in range(10):
        yield f"data: {i}\n\n"
        time.sleep(1)

@app.get("/stream")
async def stream():
    return StreamingResponse(generate(), media_type="text/event-stream")
```

---

## Deployment

### Running with Gunicorn
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Docker
```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/todo
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: todo
```

### Environment Variables
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Todo API"
    database_url: str
    jwt_secret: str
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
```

### Production Checklist
- [ ] Use HTTPS
- [ ] Set `debug=False`
- [ ] Configure proper CORS
- [ ] Use connection pooling
- [ ] Set up logging
- [ ] Configure health checks
- [ ] Set resource limits (Docker/K8s)
- [ ] Use process manager (gunicorn, uvicorn workers)

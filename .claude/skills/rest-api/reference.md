# REST API Reference Guide

## Table of Contents
1. [Advanced Query Parameters](#advanced-query-parameters)
2. [Pagination Patterns](#pagination-patterns)
3. [API Versioning](#api-versioning)
4. [Rate Limiting](#rate-limiting)
5. [OpenAPI Documentation](#openapi-documentation)

---

## Advanced Query Parameters

### Filtering
```
GET /api/{user_id}/tasks?status=pending
GET /api/{user_id}/tasks?status=completed
GET /api/{user_id}/tasks?priority=high
```

### Sorting
```
GET /api/{user_id}/tasks?sort=created&order=desc
GET /api/{user_id}/tasks?sort=title&order=asc
GET /api/{user_id}/tasks?sort=due_date&order=asc
```

### Combined Query
```
GET /api/{user_id}/tasks?status=pending&sort=created&order=desc&limit=10
```

### Field Selection
```
GET /api/{user_id}/tasks?fields=id,title,completed
GET /api/{user_id}/tasks/{id}?fields=title,description
```

---

## Pagination Patterns

### Offset-Based Pagination
```
GET /api/{user_id}/tasks?skip=0&limit=20
GET /api/{user_id}/tasks?skip=20&limit=20
GET /api/{user_id}/tasks?skip=40&limit=20
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "skip": 0,
    "limit": 20,
    "total": 100,
    "has_more": true
  }
}
```

### Cursor-Based Pagination (Recommended for large datasets)
```
GET /api/{user_id}/tasks?cursor=abc123
GET /api/{user_id}/tasks?cursor=next_cursor
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "xyz789",
    "has_more": true
  }
}
```

### Page-Based Pagination
```
GET /api/{user_id}/tasks?page=1&page_size=20
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

---

## API Versioning

### URL Path Versioning (Most Common)
```
GET /api/v1/{user_id}/tasks
GET /api/v2/{user_id}/tasks
```

### Header-Based Versioning
```
GET /api/{user_id}/tasks
Accept: application/vnd.api+json;version=1
```

### Query Parameter Versioning
```
GET /api/{user_id}/tasks?version=1
```

### Versioning Strategy

```python
from fastapi import APIRouter, Request

router = APIRouter(prefix="/api")

@router.get("/{user_id}/tasks")
async def list_tasks(request: Request, user_id: str):
    version = request.query_params.get("version", "1")

    if version == "1":
        return await list_tasks_v1(user_id)
    elif version == "2":
        return await list_tasks_v2(user_id)
    else:
        raise HTTPException(status_code=400, detail="Unsupported version")
```

---

## Rate Limiting

### Token Bucket Algorithm

```python
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
import asyncio

class RateLimiter:
    def __init__(self, rate: int, capacity: int):
        self.rate = rate  # requests per second
        self.capacity = capacity  # max tokens in bucket
        self.tokens = capacity
        self.last_update = datetime.utcnow()
        self.lock = asyncio.Lock()

    async def acquire(self, key: str) -> bool:
        async with self.lock:
            now = datetime.utcnow()
            elapsed = (now - self.last_update).total_seconds()
            self.last_update = now

            # Add tokens based on elapsed time
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.rate
            )

            if self.tokens >= 1:
                self.tokens -= 1
                return True

            return False

# Usage
limiter = RateLimiter(rate=1, capacity=10)  # 10 requests per 10 seconds

@router.get("/{user_id}/tasks")
async def list_tasks(request: Request, user_id: str):
    if not await limiter.acquire(user_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later."
        )
    return [...]
```

### Using Redis for Distributed Rate Limiting

```python
import redis
from fastapi import Request

redis_client = redis.Redis(host="localhost", port=6379, db=0)

async def rate_limit(
    request: Request,
    user_id: str,
    limit: int = 100,
    window: int = 3600  # 1 hour
):
    key = f"rate_limit:{user_id}"

    current = redis_client.get(key)
    if current and int(current) >= limit:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )

    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, window)
    pipe.execute()

    return True
```

---

## OpenAPI Documentation

### Basic Setup

```python
from fastapi import FastAPI

app = FastAPI(
    title="Todo API",
    description="REST API for managing personal tasks",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "tasks", "description": "Task CRUD operations"},
        {"name": "health", "description": "Health check endpoints"},
    ]
)
```

### Documenting Endpoints

```python
from pydantic import Field
from datetime import datetime

class TaskResponse(BaseModel):
    """Response model for a task."""
    id: int = Field(..., description="Unique task identifier")
    user_id: str = Field(..., description="Owning user ID")
    title: str = Field(..., description="Task title", min_length=1, max_length=200)
    description: str | None = Field(None, description="Task details")
    completed: bool = Field(False, description="Completion status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a task",
    description="Retrieve a specific task by its ID.",
    responses={
        200: {"description": "Task found", "model": TaskResponse},
        404: {"description": "Task not found"},
        401: {"description": "Unauthorized"},
    },
    tags=["tasks"]
)
async def get_task(task_id: int, user_id: str = Depends(get_current_user)):
    """Get a single task by ID."""
    pass
```

### Request Examples

```python
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str = Field(..., example="Buy groceries")
    description: str | None = Field(None, example="Milk, eggs, bread")

@router.post(
    "/",
    response_model=TaskResponse,
    status_code=201,
    summary="Create a task",
    description="Create a new task for the authenticated user.",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread"
                    }
                }
            }
        }
    }
)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user)
):
    """Create a new task."""
    pass
```

### Response Examples

```python
class TaskResponse(BaseModel):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "user_id": "user_123",
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread",
                    "completed": False,
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z"
                }
            ]
        }
    }
```

### Security Scheme

```python
from fastapi import FastAPI
from fastapi.openapi.models import SecurityScheme

app = FastAPI(
    title="Todo API",
    description="API with JWT authentication",
    openapi_security=[
        {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT authorization header using the Bearer scheme"
        }
    ]
)

# Or define globally
app.openapi_schema = {
    "openapi": "3.0.0",
    "info": {
        "title": "Todo API",
        "version": "1.0.0"
    },
    "components": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
    },
    "security": [{"bearerAuth": []}]
}
```

---

## Error Handling Best Practices

### Standardized Error Response

```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str

class ErrorResponse(BaseModel):
    error: str
    message: str
    code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[List[ErrorDetail]] = None

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            message=str(exc) if DEBUG else "An unexpected error occurred",
            code="INTERNAL_ERROR"
        ).model_dump()
    )
```

### Common Error Codes

```python
ERROR_CODES = {
    "VALIDATION_ERROR": {
        "status": 422,
        "message": "Request validation failed"
    },
    "UNAUTHORIZED": {
        "status": 401,
        "message": "Authentication required"
    },
    "FORBIDDEN": {
        "status": 403,
        "message": "Access denied"
    },
    "NOT_FOUND": {
        "status": 404,
        "message": "Resource not found"
    },
    "RATE_LIMITED": {
        "status": 429,
        "message": "Too many requests"
    },
    "INTERNAL_ERROR": {
        "status": 500,
        "message": "An unexpected error occurred"
    },
}
```

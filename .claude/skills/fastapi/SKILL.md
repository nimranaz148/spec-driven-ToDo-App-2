---
name: fastapi
description: FastAPI web framework patterns and best practices. Use when building REST APIs, adding endpoints, or configuring FastAPI application for the Todo backend.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

# FastAPI Skill

## Quick Reference

FastAPI is a modern Python web framework for building APIs with automatic documentation.

## Basic App Structure

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Todo API",
    description="REST API for Todo application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## Routing Patterns

```python
from fastapi import APIRouter, HTTPException, Depends, Query

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])

@router.get("/")
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: str = Depends(get_current_user)
):
    """List tasks with pagination."""
    pass

@router.post("/")
async def create_task(
    task: TaskCreate,
    user_id: str = Depends(get_current_user)
):
    """Create a new task."""
    pass

@router.get("/{task_id}")
async def get_task(
    task_id: int,
    user_id: str = Depends(get_current_user)
):
    """Get a specific task."""
    pass
```

## Dependency Injection

```python
from typing import Annotated

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> str:
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload.get("sub")

# Use in routes
@router.get("/")
async def list_tasks(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pass
```

## Error Handling

```python
from fastapi import HTTPException, status

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Raise errors in routes
if not task:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )
```

## Request Models (Pydantic)

```python
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)

class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    completed: bool | None = None
```

## Response Models

```python
from pydantic import BaseModel
from datetime import datetime

class TaskResponse(BaseModel):
    id: int
    user_id: str
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=list[TaskResponse])
async def list_tasks():
    pass
```

## Running the Server

```bash
uvicorn main:app --reload --port 8000
# Or with hot reload
uvicorn main:app --reload
```

## For Detailed Reference

See [REFERENCE.md](REFERENCE.md) for:
- Advanced routing patterns
- Middleware configuration
- Testing FastAPI apps
- Performance optimization
- Deployment options

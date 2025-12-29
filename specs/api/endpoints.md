# REST API Endpoints

## Base URL
- Development: http://localhost:8000
- Production: https://api.example.com

## Authentication
All endpoints require JWT token in header:
```
Authorization: Bearer <token>
```

## Endpoints

### GET /api/{user_id}/tasks
List all tasks for authenticated user.

**Query Parameters:**
- status: "all" | "pending" | "completed" (default: "all")
- sort: "created" | "title" | "due_date" (default: "created")

**Response:**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2025-12-24T10:00:00Z",
      "updated_at": "2025-12-24T10:00:00Z"
    }
  ]
}
```

### POST /api/{user_id}/tasks
Create a new task.

**Request Body:**
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-24T10:00:00Z",
  "updated_at": "2025-12-24T10:00:00Z"
}
```

### GET /api/{user_id}/tasks/{id}
Get task details.

**Response:**
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-24T10:00:00Z",
  "updated_at": "2025-12-24T10:00:00Z"
}
```

### PUT /api/{user_id}/tasks/{id}
Update a task.

**Request Body:**
```json
{
  "title": "Buy groceries and fruits",
  "description": "Updated description"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Buy groceries and fruits",
  "description": "Updated description",
  "completed": false,
  "created_at": "2025-12-24T10:00:00Z",
  "updated_at": "2025-12-24T11:00:00Z"
}
```

### DELETE /api/{user_id}/tasks/{id}
Delete a task.

**Response:**
```json
{
  "message": "Task deleted successfully",
  "id": 1
}
```

### PATCH /api/{user_id}/tasks/{id}/complete
Toggle task completion status.

**Response:**
```json
{
  "id": 1,
  "title": "Buy groceries",
  "completed": true,
  "updated_at": "2025-12-24T11:00:00Z"
}
```

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Invalid or missing authentication token"
}
```

### 404 Not Found
```json
{
  "detail": "Task not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

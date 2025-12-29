# API Documentation

**Version**: 1.0.0
**Base URL**: `http://localhost:8000` (development) | `https://api.yourdomain.com` (production)
**Last Updated**: 2025-12-27

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Authentication Endpoints](#authentication-endpoints)
  - [Task Endpoints](#task-endpoints)
  - [Health Check](#health-check)
- [Request/Response Examples](#requestresponse-examples)
- [Status Codes](#status-codes)
- [Changelog](#changelog)

---

## Overview

The Todo API is a RESTful web service built with FastAPI that provides secure task management functionality. All endpoints (except authentication) require JWT token authentication.

### Key Features

- JWT-based authentication with token blacklisting
- User data isolation - users can only access their own tasks
- Rate limiting (60 requests/minute per user)
- Comprehensive input validation
- Structured error responses
- OpenAPI/Swagger documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Authentication

### JWT Bearer Token

All protected endpoints require a JWT token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

### Obtaining a Token

1. Register a new account via `POST /api/auth/register`
2. Login via `POST /api/auth/login`
3. Use the `access_token` from the response in subsequent requests

### Token Properties

- **Algorithm**: HS256
- **Expiration**: 7 days
- **Payload**: `{ "sub": user_id, "email": user_email, "exp": expiration, "iat": issued_at }`

### Token Invalidation

Tokens are invalidated (blacklisted) when:
- User logs out via `POST /api/auth/logout`
- Token expires naturally after 7 days

---

## Rate Limiting

All authenticated endpoints are rate-limited to prevent abuse.

### Limits

- **Rate**: 60 requests per minute per authenticated user
- **Window**: 60 seconds (rolling window)

### Rate Limit Headers

Every response includes rate limit information:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1735315200
```

- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets

### Rate Limit Exceeded

When the rate limit is exceeded, the API returns:

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
  "detail": "Rate limit exceeded. Please try again later.",
  "error_code": "RATE_LIMIT_EXCEEDED"
}
```

---

## Error Handling

### Error Response Format

All errors follow a consistent JSON structure:

```json
{
  "detail": "Human-readable error message"
}
```

### Common Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | Bad Request | Invalid request parameters or body |
| 401 | Unauthorized | Missing or invalid authentication token |
| 403 | Forbidden | Valid token but insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Resource already exists (e.g., duplicate email) |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |

### Validation Errors (422)

Validation errors include detailed field-level information:

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    },
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

---

## Endpoints

### Authentication Endpoints

#### POST /api/auth/register

Register a new user account.

**Request Body:**

```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "SecurePass123!"
}
```

**Validation Rules:**

- `email`: Valid email format, unique across all users
- `name`: 1-255 characters
- `password`: 8-128 characters

**Success Response (201 Created):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2025-12-27T10:00:00Z"
  }
}
```

**Error Responses:**

- `400 Bad Request`: Invalid input format
- `409 Conflict`: Email already registered

**Example:**

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "SecurePass123!"
  }'
```

---

#### POST /api/auth/login

Authenticate a user and receive a JWT token.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Success Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2025-12-27T10:00:00Z"
  }
}
```

**Error Responses:**

- `401 Unauthorized`: Invalid email or password

**Example:**

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

---

#### POST /api/auth/logout

Logout the current user and invalidate their JWT token.

**Headers:**

```http
Authorization: Bearer <your_jwt_token>
```

**Success Response (200 OK):**

```json
{
  "message": "Successfully logged out"
}
```

**Error Responses:**

- `401 Unauthorized`: Invalid or expired token

**Example:**

```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

#### GET /api/auth/me

Get the current authenticated user's information.

**Headers:**

```http
Authorization: Bearer <your_jwt_token>
```

**Success Response (200 OK):**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": null
}
```

**Error Responses:**

- `401 Unauthorized`: Invalid or expired token

**Example:**

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### Task Endpoints

All task endpoints require authentication and enforce user data isolation.

#### GET /api/{user_id}/tasks

List all tasks for the authenticated user with optional filtering and pagination.

**Path Parameters:**

- `user_id` (string): User ID (must match authenticated user)

**Query Parameters:**

- `completed` (boolean, optional): Filter by completion status
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum records to return (default: 100, max: 1000)

**Headers:**

```http
Authorization: Bearer <your_jwt_token>
```

**Success Response (200 OK):**

```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread, and cheese",
      "completed": false,
      "created_at": "2025-12-27T10:00:00Z",
      "updated_at": "2025-12-27T10:00:00Z"
    },
    {
      "id": 2,
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Finish project report",
      "description": "Complete the Q4 report for management",
      "completed": true,
      "created_at": "2025-12-26T15:30:00Z",
      "updated_at": "2025-12-27T09:00:00Z"
    }
  ],
  "total": 2
}
```

**Error Responses:**

- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Attempting to access another user's tasks

**Example:**

```bash
# Get all tasks
curl -X GET http://localhost:8000/api/550e8400-e29b-41d4-a716-446655440000/tasks \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Get only incomplete tasks
curl -X GET "http://localhost:8000/api/550e8400-e29b-41d4-a716-446655440000/tasks?completed=false" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Get with pagination
curl -X GET "http://localhost:8000/api/550e8400-e29b-41d4-a716-446655440000/tasks?skip=10&limit=20" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

#### GET /api/{user_id}/tasks/{task_id}

Get a single task by ID.

**Path Parameters:**

- `user_id` (string): User ID (must match authenticated user)
- `task_id` (integer): Task ID

**Headers:**

```http
Authorization: Bearer <your_jwt_token>
```

**Success Response (200 OK):**

```json
{
  "id": 1,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, and cheese",
  "completed": false,
  "created_at": "2025-12-27T10:00:00Z",
  "updated_at": "2025-12-27T10:00:00Z"
}
```

**Error Responses:**

- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Attempting to access another user's task
- `404 Not Found`: Task does not exist

**Example:**

```bash
curl -X GET http://localhost:8000/api/550e8400-e29b-41d4-a716-446655440000/tasks/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

#### POST /api/{user_id}/tasks

Create a new task for the authenticated user.

**Path Parameters:**

- `user_id` (string): User ID (must match authenticated user)

**Headers:**

```http
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, and cheese"
}
```

**Validation Rules:**

- `title`: Required, 1-200 characters
- `description`: Optional, max 1000 characters

**Success Response (201 Created):**

```json
{
  "id": 1,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, and cheese",
  "completed": false,
  "created_at": "2025-12-27T10:00:00Z",
  "updated_at": "2025-12-27T10:00:00Z"
}
```

**Error Responses:**

- `400 Bad Request`: Invalid input format
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Attempting to create task for another user
- `422 Unprocessable Entity`: Validation error

**Example:**

```bash
curl -X POST http://localhost:8000/api/550e8400-e29b-41d4-a716-446655440000/tasks \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread, and cheese"
  }'
```

---

#### PUT /api/{user_id}/tasks/{task_id}

Update an existing task.

**Path Parameters:**

- `user_id` (string): User ID (must match authenticated user)
- `task_id` (integer): Task ID

**Headers:**

```http
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Request Body:**

All fields are optional. Only provided fields will be updated.

```json
{
  "title": "Buy groceries and fruits",
  "description": "Updated shopping list with fruits",
  "completed": false
}
```

**Validation Rules:**

- `title`: Optional, 1-200 characters if provided
- `description`: Optional, max 1000 characters if provided
- `completed`: Optional, boolean if provided

**Success Response (200 OK):**

```json
{
  "id": 1,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries and fruits",
  "description": "Updated shopping list with fruits",
  "completed": false,
  "created_at": "2025-12-27T10:00:00Z",
  "updated_at": "2025-12-27T11:30:00Z"
}
```

**Error Responses:**

- `400 Bad Request`: Invalid input format
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Attempting to update another user's task
- `404 Not Found`: Task does not exist
- `422 Unprocessable Entity`: Validation error

**Example:**

```bash
curl -X PUT http://localhost:8000/api/550e8400-e29b-41d4-a716-446655440000/tasks/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries and fruits",
    "description": "Updated shopping list with fruits"
  }'
```

---

#### DELETE /api/{user_id}/tasks/{task_id}

Delete a task.

**Path Parameters:**

- `user_id` (string): User ID (must match authenticated user)
- `task_id` (integer): Task ID

**Headers:**

```http
Authorization: Bearer <your_jwt_token>
```

**Success Response (204 No Content):**

No response body.

**Error Responses:**

- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Attempting to delete another user's task
- `404 Not Found`: Task does not exist

**Example:**

```bash
curl -X DELETE http://localhost:8000/api/550e8400-e29b-41d4-a716-446655440000/tasks/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

#### PATCH /api/{user_id}/tasks/{task_id}/complete

Toggle task completion status (complete ↔ incomplete).

**Path Parameters:**

- `user_id` (string): User ID (must match authenticated user)
- `task_id` (integer): Task ID

**Headers:**

```http
Authorization: Bearer <your_jwt_token>
```

**Success Response (200 OK):**

```json
{
  "id": 1,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, and cheese",
  "completed": true,
  "created_at": "2025-12-27T10:00:00Z",
  "updated_at": "2025-12-27T12:00:00Z"
}
```

**Error Responses:**

- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Attempting to modify another user's task
- `404 Not Found`: Task does not exist

**Example:**

```bash
curl -X PATCH http://localhost:8000/api/550e8400-e29b-41d4-a716-446655440000/tasks/1/complete \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### Health Check

#### GET /health

Check if the API is running and healthy.

**No authentication required.**

**Success Response (200 OK):**

```json
{
  "status": "healthy"
}
```

**Example:**

```bash
curl -X GET http://localhost:8000/health
```

---

#### GET /

Root endpoint with API information.

**No authentication required.**

**Success Response (200 OK):**

```json
{
  "name": "Todo API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

**Example:**

```bash
curl -X GET http://localhost:8000/
```

---

## Request/Response Examples

### Complete User Flow

#### 1. Register a New User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "name": "Alice Johnson",
    "password": "SecurePassword123!"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJlbWFpbCI6ImFsaWNlQGV4YW1wbGUuY29tIiwiZXhwIjoxNzM1OTIwMDAwLCJpYXQiOjE3MzUzMTUyMDB9.signature",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "alice@example.com",
    "name": "Alice Johnson",
    "created_at": "2025-12-27T10:00:00Z"
  }
}
```

#### 2. Create a Task

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
USER_ID="550e8400-e29b-41d4-a716-446655440000"

curl -X POST http://localhost:8000/api/$USER_ID/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Write API documentation",
    "description": "Document all API endpoints with examples"
  }'
```

Response:
```json
{
  "id": 1,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Write API documentation",
  "description": "Document all API endpoints with examples",
  "completed": false,
  "created_at": "2025-12-27T10:05:00Z",
  "updated_at": "2025-12-27T10:05:00Z"
}
```

#### 3. List All Tasks

```bash
curl -X GET http://localhost:8000/api/$USER_ID/tasks \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Write API documentation",
      "description": "Document all API endpoints with examples",
      "completed": false,
      "created_at": "2025-12-27T10:05:00Z",
      "updated_at": "2025-12-27T10:05:00Z"
    }
  ],
  "total": 1
}
```

#### 4. Mark Task as Complete

```bash
curl -X PATCH http://localhost:8000/api/$USER_ID/tasks/1/complete \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "id": 1,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Write API documentation",
  "description": "Document all API endpoints with examples",
  "completed": true,
  "created_at": "2025-12-27T10:05:00Z",
  "updated_at": "2025-12-27T12:00:00Z"
}
```

#### 5. Logout

```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "message": "Successfully logged out"
}
```

---

## Status Codes

### Success Codes

| Code | Description | Usage |
|------|-------------|-------|
| 200 | OK | Successful GET, PUT, PATCH, POST (logout) |
| 201 | Created | Successful POST (register, create task) |
| 204 | No Content | Successful DELETE |

### Client Error Codes

| Code | Description | Common Causes |
|------|-------------|---------------|
| 400 | Bad Request | Malformed JSON, invalid data types |
| 401 | Unauthorized | Missing token, expired token, invalid token |
| 403 | Forbidden | Valid token but accessing another user's data |
| 404 | Not Found | Task does not exist |
| 409 | Conflict | Email already registered |
| 422 | Unprocessable Entity | Validation errors (too short, too long, wrong format) |
| 429 | Too Many Requests | Rate limit exceeded |

### Server Error Codes

| Code | Description | Action |
|------|-------------|--------|
| 500 | Internal Server Error | Contact support, check logs |
| 503 | Service Unavailable | Service temporarily down |

---

## Changelog

### Version 1.0.0 (2025-12-27)

**Initial Release**

- Authentication endpoints (register, login, logout, me)
- Task CRUD endpoints (create, read, update, delete)
- Task completion toggle endpoint
- Rate limiting (60 req/min per user)
- User data isolation
- Comprehensive error handling
- OpenAPI/Swagger documentation

---

## Support

For issues or questions:

1. Check the [Troubleshooting Guide](../README.md#troubleshooting)
2. Review the [Security Documentation](security.md)
3. Consult the [Deployment Guide](deployment.md)
4. Open an issue in the repository

---

**Last Updated**: 2025-12-27
**Version**: 1.0.0
**Generated with**: Spec-Kit Plus

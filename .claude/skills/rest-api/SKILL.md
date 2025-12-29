---
name: rest-api
description: REST API design principles and implementation patterns. Use when designing API endpoints, creating API clients, or implementing HTTP communication between frontend and backend.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

# REST API Skill

## Quick Reference

REST (Representational State Transfer) is an architectural style for designing networked applications.

## API Endpoints (Based on Spec)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/{user_id}/tasks | List all tasks |
| POST | /api/{user_id}/tasks | Create a task |
| GET | /api/{user_id}/tasks/{id} | Get task details |
| PUT | /api/{user_id}/tasks/{id} | Update a task |
| DELETE | /api/{user_id}/tasks/{id} | Delete a task |
| PATCH | /api/{user_id}/tasks/{id}/complete | Toggle completion |

## HTTP Methods

- **GET** - Retrieve resources (safe, idempotent)
- **POST** - Create new resources (not idempotent)
- **PUT** - Update/replace entire resource (idempotent)
- **PATCH** - Partial update (not idempotent)
- **DELETE** - Remove resource (idempotent)

## Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST (new resource) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Not user's resource |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

## Request Format

### Headers
```
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
Accept: application/json
```

### Body (POST/PUT/PATCH)
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false
}
```

## Response Format

### Success (200/201)
```json
{
  "id": 1,
  "user_id": "user_123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Error (4xx/5xx)
```json
{
  "detail": "Task not found",
  "code": "NOT_FOUND"
}
```

## For Detailed Reference

See [REFERENCE.md](REFERENCE.md) for:
- Advanced query parameters
- Pagination patterns
- API versioning
- Rate limiting
- OpenAPI documentation

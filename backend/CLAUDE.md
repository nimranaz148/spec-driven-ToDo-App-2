# Backend Guidelines

## Stack
- FastAPI
- SQLModel (ORM)
- Neon PostgreSQL
- JWT for auth verification

## Project Structure
- `main.py` - FastAPI app entry point
- `models.py` - SQLModel database models
- `routes/` - API route handlers
- `db.py` - Database connection
- `auth.py` - JWT verification middleware

## Coupling
- Part of monorepo: @CLAUDE.md (root)
- Frontend counterpart: @frontend/CLAUDE.md
- Specs: @specs/api/endpoints.md, @specs/database/schema.md

## API Conventions
- All routes under `/api/`
- Return JSON responses
- Use Pydantic models for request/response
- Handle errors with HTTPException

## Database
- Use SQLModel for all database operations
- Connection string from environment variable: DATABASE_URL
- SSL required for Neon Serverless PostgreSQL

## JWT Verification
- Extract token from Authorization header
- Verify using BETTER_AUTH_SECRET
- Extract user_id from token payload
- Filter all queries by authenticated user_id

## Library Documentation (Context 7 MCP)
**ALWAYS** use Context 7 MCP for up-to-date library docs:

**Context 7 HTTP Transport:**
- URL: `https://mcp.context7.com/mcp`
- API Key: Configured at user level (ctx7sk-...)

**Available libraries:**
- FastAPI: `context7://fastapi/latest`
- SQLModel: `context7://sqlmodel/latest`
- Pydantic: `context7://pydantic/latest`

**When implementing backend:**
1. Fetch FastAPI patterns: "Use Context 7 to get latest FastAPI routing and dependency injection patterns"
2. Fetch SQLModel patterns: "Fetch SQLModel relationship and session management docs"
3. Fetch Pydantic patterns: "Get Pydantic v2 validation patterns"

**Example prompt:**
> "Fetch Context 7 docs for FastAPI best practices for JWT authentication middleware with Depends()"

## Running
```bash
uvicorn main:app --reload --port 8000
```

## Key Endpoints
- GET /api/{user_id}/tasks - List tasks
- POST /api/{user_id}/tasks - Create task
- GET /api/{user_id}/tasks/{id} - Get task
- PUT /api/{user_id}/tasks/{id} - Update task
- DELETE /api/{user_id}/tasks/{id} - Delete task
- PATCH /api/{user_id}/tasks/{id}/complete - Toggle completion

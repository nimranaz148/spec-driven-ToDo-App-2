# Quickstart — AI-Powered Todo Chatbot

## Prerequisites
- Python 3.13 with uv (or pip)
- Node.js 22+ with pnpm/npm
- Postgres connection (Neon) configured in `.env`
- Gemini API key available (get one at https://aistudio.google.com/apikey)

## Setup Steps

1. **Install backend deps**
   ```bash
   cd backend
   uv pip install -r requirements.txt  # or uv pip sync pyproject.toml
   ```

2. **Install frontend deps**
   ```bash
   cd frontend
   npm install
   ```

3. **Environment variables**

   Copy the example files and fill in your values:

   ```bash
   # Backend
   cp backend/.env.example backend/.env

   # Frontend
   cp frontend/.env.local.example frontend/.env.local
   ```

   **Backend (`backend/.env`):**
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@host/database?sslmode=require
   BETTER_AUTH_SECRET=your-secure-jwt-secret-here
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   ENVIRONMENT=development
   GEMINI_API_KEY=your-gemini-api-key
   GEMINI_MODEL=gemini-2.5-flash
   RATE_LIMIT_PER_MINUTE=30
   ```

   **Frontend (`frontend/.env.local`):**
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_APP_URL=http://localhost:3000
   BETTER_AUTH_SECRET=your-secure-jwt-secret-here  # Must match backend
   DATABASE_URL=postgresql://user:password@host/database?sslmode=require
   ```

4. **Database migrations**
   ```bash
   cd backend
   alembic upgrade head
   ```

5. **Run backend API server**
   ```bash
   cd backend
   uvicorn src.main:app --reload --port 8000
   ```

6. **Run MCP server (separate terminal, required for AI chat)**

   The MCP server exposes task CRUD tools to the AI agent:
   ```bash
   cd backend
   python -m src.mcp_server
   ```

   **Note:** The MCP server must be running for the chat endpoint to function. It runs on a separate port and communicates with the main FastAPI server.

7. **Start frontend**
   ```bash
   cd frontend
   npm run dev
   ```

## Quick Start Commands (Combined)

For development, you can run all services with a single command:

```bash
# Terminal 1: Backend API + MCP Server
cd backend && uvicorn src.main:app --reload --port 8000 &
cd backend && python -m src.mcp_server &

# Terminal 2: Frontend
cd frontend && npm run dev
```

Or use the convenience script (if available):
```bash
make chat-dev  # Starts backend, MCP server, and frontend
```

## Testing

### Backend Tests
```bash
cd backend

# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests (requires database)
pytest tests/integration/

# Contract tests
pytest tests/contract/
```

### Frontend Tests
```bash
cd frontend

# Unit tests
npm test

# E2E tests (Playwright)
npm run test:e2e
```

## Testing the Chat Endpoint

Once all services are running:

1. **Get a JWT token** (via frontend login or API):
   ```bash
   # Login via API and extract token
   curl -X POST http://localhost:3000/api/auth/sign-in/email \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password123"}'
   ```

2. **Send a chat message**:
   ```bash
   curl -X POST "http://localhost:8000/api/{user_id}/chat" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message": "Add a task to buy groceries"}'
   ```

3. **Expected response**:
   ```json
   {
     "conversation_id": 1,
     "response": "I've created a task 'Buy groceries' for you!",
     "tool_calls": [
       {
         "tool": "create_task",
         "parameters": {"title": "Buy groceries"},
         "result": {"id": 42, "title": "Buy groceries", "completed": false}
       }
     ]
   }
   ```

## Usage Flow

1. Sign up / log in through Better Auth-enabled frontend.
2. Navigate to `/dashboard/chat`.
3. Send a natural language message (e.g., "Add a task to call Mom").
4. Chat UI displays conversation history from backend and streams assistant response.
5. The AI can:
   - Create tasks: "Add a task to buy milk"
   - List tasks: "What are my pending tasks?"
   - Complete tasks: "Mark task 3 as done"
   - Update tasks: "Change task 2 to 'Buy organic milk'"
   - Delete tasks: "Remove task 5" (with confirmation for destructive actions)
6. View and manage tasks in the main dashboard.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Chat returns 500 error | Ensure MCP server is running (`python -m src.mcp_server`) |
| 401 Unauthorized | Check JWT token is valid and not expired |
| 403 Forbidden | Verify user_id in URL matches authenticated user |
| 429 Too Many Requests | Rate limit exceeded (30 req/min); wait and retry |
| Gemini API errors | Verify `GEMINI_API_KEY` is set correctly |

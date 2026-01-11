# MCP Server - Separate Process Setup ✅

## Architecture

The MCP server now runs as a **separate process** on port 8001, just like in todo-web-hackthon:

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Port 3000)                     │
│  - Next.js App                                               │
│  - Better Auth → Neon PostgreSQL                             │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP Requests
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                  Backend API (Port 8000)                     │
│  - FastAPI                                                   │
│  - REST endpoints: /api/tasks, /api/chat, etc.              │
│  - AI Agent (OpenAI Agents SDK + Gemini)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │ MCP Protocol
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                  MCP Server (Port 8001)                      │
│  - FastMCP HTTP Server                                       │
│  - Tools: create_task, list_tasks, update_task, etc.        │
│  - Direct database access → Neon PostgreSQL                  │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Backend .env
```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_t6hbeXkNYa0M@ep-misty-term-a47frtaa-pooler.us-east-1.aws.neon.tech/neondb?ssl=require
GEMINI_API_KEY=AIzaSyBEvjCrL82gnb7UeMqxWCaYUnEtpEg3VGo
GEMINI_MODEL=gemini/gemini-2.5-flash
MCP_SERVER_URL=http://localhost:8001/mcp
MCP_SERVER_PORT=8001
```

### Agent Config (src/agent/config.py)
```python
mcp_server_url: str = Field(
    default="http://localhost:8001/mcp",
    description="URL of the MCP server endpoint (FastMCP HTTP transport on separate port)",
)
```

## How to Run

### Option 1: Run Services Separately (Recommended for Development)

**Terminal 1 - Backend API:**
```bash
cd spec-driven-ToDo-App-II
make backend-dev
# Or: cd backend && uv run uvicorn src.main:app --reload --port 8000
```

**Terminal 2 - MCP Server:**
```bash
cd spec-driven-ToDo-App-II
make mcp-dev
# Or: cd backend && uv run python -m src.mcp_server
```

**Terminal 3 - Frontend:**
```bash
cd spec-driven-ToDo-App-II
make frontend-dev
# Or: cd frontend && npm run dev
```

### Option 2: Run All Services in Background

```bash
cd spec-driven-ToDo-App-II
make chat-dev-bg
```

This starts all three services in the background with logs:
- `backend.log` - Backend API logs
- `mcp.log` - MCP server logs
- `frontend.log` - Frontend logs

To stop all services:
```bash
make stop
```

## Verification

### 1. Check Backend API
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### 2. Check MCP Server
```bash
curl http://localhost:8001/mcp
# Expected: MCP server response (not 404)
```

### 3. Check Frontend
Open http://localhost:3000 in browser

### 4. Test Full Flow
1. Sign up/Sign in at http://localhost:3000
2. Go to dashboard
3. Open chat
4. Send message: "Show me my tasks"
5. Should get AI response using MCP tools

## MCP Server Details

### Entry Point
`backend/src/mcp_server.py` with `if __name__ == "__main__":`

### Port Configuration
- Default: 8001
- Override via `MCP_SERVER_PORT` environment variable

### Available Tools
1. **create_task** - Create a new task
2. **list_tasks** - List tasks with filtering
3. **update_task** - Update task fields
4. **complete_task** - Toggle completion status
5. **delete_task** - Delete a task

### User Isolation
User ID is passed via query parameter:
```
http://localhost:8001/mcp?user_id=<user_id>
```

The MCP server extracts `user_id` from the request and ensures all operations are scoped to that user.

## Troubleshooting

### MCP Server Won't Start
```bash
# Check if port 8001 is already in use
lsof -i:8001

# Kill existing process
pkill -f "python -m src.mcp_server"

# Restart
make mcp-dev
```

### Agent Can't Connect to MCP
1. Verify MCP server is running: `curl http://localhost:8001/mcp`
2. Check `MCP_SERVER_URL` in `.env`: `http://localhost:8001/mcp`
3. Check backend logs for connection errors
4. Restart both backend and MCP server

### Database Connection Issues
1. Verify Neon database is active
2. Check `DATABASE_URL` format: `postgresql+asyncpg://...?ssl=require`
3. Test connection: `cd backend && uv run python -c "from src.db import engine; print('OK')"`

## Comparison with todo-web-hackthon

Both projects now have identical architecture:
- ✅ Backend API on port 8000
- ✅ MCP Server on port 8001 (separate process)
- ✅ Frontend on port 3000
- ✅ Neon PostgreSQL database
- ✅ OpenAI Agents SDK with Gemini
- ✅ FastMCP tools for task management

## Files Modified

1. ✅ `backend/src/main.py` - Removed MCP mount, added comment
2. ✅ `backend/src/agent/config.py` - Changed default to port 8001
3. ✅ `backend/.env` - Added MCP_SERVER_URL and MCP_SERVER_PORT
4. ✅ `Makefile` - Already has mcp-dev command

## Next Steps

1. **Stop current backend** (if running)
2. **Start all three services:**
   ```bash
   # Terminal 1
   make backend-dev
   
   # Terminal 2
   make mcp-dev
   
   # Terminal 3
   make frontend-dev
   ```
3. **Test the application**
4. **Verify chat works with AI agent**

## Status
✅ **MCP server configured to run on port 8001**
✅ **Backend API on port 8000**
✅ **Agent connects to MCP via http://localhost:8001/mcp**
✅ **Ready to start all services**

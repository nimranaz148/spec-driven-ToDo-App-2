# Neon Database Setup - Complete ✅

## Issues Fixed

### 1. Backend FastMCP Error
**Problem:** `AttributeError: 'FastMCP' object has no attribute 'session_manager'`
**Fix:** Removed incorrect session_manager usage from lifespan function

### 2. Database URL Format
**Backend:** Changed to `postgresql+asyncpg://...?ssl=require` (for asyncpg)
**Frontend:** Using `postgresql://...?sslmode=require` (for pg/Better Auth)

### 3. Better Auth Connection Timeouts
**Problem:** `ETIMEDOUT` errors when connecting to Neon
**Fix:** Optimized connection pool settings:
- Reduced connection timeout to 10s
- Smaller pool size (max: 3)
- Added query and statement timeouts

## Configuration Summary

### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_t6hbeXkNYa0M@ep-misty-term-a47frtaa-pooler.us-east-1.aws.neon.tech/neondb?ssl=require
BETTER_AUTH_SECRET=0Of0PmHBRmcTpXCFrBAZkLVYmEDh8A5c
GEMINI_API_KEY=AIzaSyBEvjCrL82gnb7UeMqxWCaYUnEtpEg3VGo
```

### Frontend (.env)
```env
DATABASE_URL=postgresql://neondb_owner:npg_t6hbeXkNYa0M@ep-misty-term-a47frtaa-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=0Of0PmHBRmcTpXCFrBAZkLVYmEDh8A5c
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## Neon Database Details
- **Host:** ep-misty-term-a47frtaa-pooler.us-east-1.aws.neon.tech
- **Database:** neondb
- **User:** neondb_owner
- **SSL:** Required
- **Region:** us-east-1

## How to Restart Services

### Stop Current Services
```bash
# Stop backend
pkill -f "uvicorn src.main:app"

# Stop frontend
pkill -f "next dev"
```

### Start Backend
```bash
cd spec-driven-ToDo-App-II/backend
uv run uvicorn src.main:app --reload --port 8000
```

### Start Frontend
```bash
cd spec-driven-ToDo-App-II/frontend
npm run dev
```

## Verification Steps

1. **Check Backend Health:**
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

2. **Check Frontend:**
- Open http://localhost:3000
- Try to sign up/sign in
- Should NOT see ETIMEDOUT errors

3. **Check Database Tables:**
Better Auth will automatically create:
- `user` table
- `session` table  
- `account` table
- `verification` table

## OpenAI Agent SDK & FastMCP Setup

### Backend Dependencies (pyproject.toml)
```toml
"openai>=1.0.0"
"openai-agents>=0.6.0"
"mcp>=1.0.0"
"fastmcp>=2.0.0,<3"
"psycopg2-binary>=2.9.0"  # For MCP sync operations
```

### MCP Server
- **Endpoint:** http://localhost:8000/mcp
- **Tools:** create_task, list_tasks, update_task, complete_task, delete_task
- **User Isolation:** Via user_id query parameter

### Agent Configuration
Located in `backend/src/routes/chat.py`:
- Uses OpenAI Agents SDK
- Connects to FastMCP via MCPServerStreamableHttp
- Gemini 2.5 Flash model via LiteLLM

## Troubleshooting

### If Backend Still Won't Start
```bash
cd spec-driven-ToDo-App-II/backend
# Check dependencies
uv pip list | grep -E "(fastmcp|openai|asyncpg)"

# Reinstall if needed
uv pip install -e .
```

### If Frontend Still Gets ETIMEDOUT
1. Check Neon dashboard: https://console.neon.tech
2. Verify database is active (not suspended)
3. Check connection string is correct
4. Try increasing timeout in `frontend/src/lib/auth.ts`

### If MCP Tools Don't Work
1. Check MCP endpoint: http://localhost:8000/mcp
2. Verify user_id is passed in query params
3. Check backend logs for MCP tool errors

## Next Steps

1. Restart both services
2. Test sign-up/sign-in
3. Test chat functionality
4. Verify MCP tools work via chat

## Status
✅ Database URLs configured for Neon
✅ Backend FastMCP error fixed
✅ Better Auth connection pool optimized
✅ OpenAI Agent SDK configured
✅ FastMCP tools exposed
✅ Ready to restart services

# Better Auth Database Connection Fix

## Problem
Frontend Better Auth is configured to use **Neon PostgreSQL** (cloud database) which is timing out with `ETIMEDOUT` error.

## Root Cause
```
DATABASE_URL=postgresql://neondb_owner:npg_t6hbeXkNYa0M@ep-misty-term-a47frtaa-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
```

This Neon database connection is either:
1. Not accessible (firewall/network issue)
2. Credentials expired
3. Database doesn't exist or was deleted

## Solution Options

### Option 1: Use Local PostgreSQL (Recommended for Development)

1. **Start local PostgreSQL with Docker:**
```bash
docker run --name todo-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=todo_db \
  -p 5432:5432 \
  -d postgres:15
```

2. **Update frontend/.env:**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_db
```

3. **Restart frontend:**
```bash
cd frontend
npm run dev
```

### Option 2: Fix Neon Connection

1. **Login to Neon Dashboard:** https://console.neon.tech
2. **Verify database exists and is active**
3. **Get new connection string** from dashboard
4. **Update frontend/.env** with new credentials

### Option 3: Use SQLite (Simplest for Development)

Better Auth doesn't support SQLite directly, but you can use a local PostgreSQL or switch to a different auth solution.

## Quick Fix (Use Docker PostgreSQL)

Run this command to set up everything:

```bash
# From project root
cd spec-driven-ToDo-App-II

# Start PostgreSQL
docker run --name todo-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=todo_db \
  -p 5432:5432 \
  -d postgres:15

# Update frontend .env
cat > frontend/.env << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_db
BETTER_AUTH_SECRET=0Of0PmHBRmcTpXCFrBAZkLVYmEDh8A5c
BETTER_AUTH_URL=http://localhost:3000
NODE_ENV=development
EOF

# Restart frontend
cd frontend
npm run dev
```

## Verification

After applying the fix, you should see:
- ✅ No `ETIMEDOUT` errors
- ✅ Better Auth tables created automatically
- ✅ Sign-in/sign-up working

## Better Auth Tables

Better Auth will automatically create these tables:
- `user` - User accounts
- `session` - Active sessions
- `account` - OAuth accounts (if using social login)
- `verification` - Email verification tokens

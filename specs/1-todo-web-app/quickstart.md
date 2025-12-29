# Quickstart Guide: Todo Web Application

**Feature**: Todo Full-Stack Web Application
**Version**: 1.0.0
**Date**: 2025-12-26

---

## Prerequisites

- Node.js 20+
- Python 3.13+
- UV (Python package manager)
- PostgreSQL (Neon Serverless)

---

## Environment Setup

### 1. Clone and Install

```bash
# Frontend
cd frontend
npm install

# Backend
cd backend
uv pip install -r requirements.txt
```

### 2. Environment Variables

**Backend (.env)**
```env
DATABASE_URL=postgresql://user:password@host/database
BETTER_AUTH_SECRET=your-jwt-secret-here
CORS_ORIGIN=http://localhost:3000
```

**Frontend (.env.local)**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-jwt-secret-here
```

### 3. Database Setup

```bash
# Backend
cd backend
uv run python -c "from db import create_tables; create_tables()"
```

---

## Running the Application

### Development

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Production Build

```bash
# Frontend
cd frontend
npm run build

# Backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## Default Users

No default users. Register via the UI.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| CORS errors | Check CORS_ORIGIN matches frontend URL |
| DB connection failed | Verify DATABASE_URL is correct |
| JWT errors | Ensure BETTER_AUTH_SECRET matches |

---

*Generated with Spec-Kit Plus*
*Version*: 1.0.0
*Date*: 2025-12-26

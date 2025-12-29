# Implementation Plan: Todo Web Application - Phase 2

**Branch**: `1-todo-web-app` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from Phase 2 requirements and constitution

## Summary

Build a production-ready, full-stack web application that transforms the Phase 1 console app into a multi-user web platform with persistent storage. The implementation follows a spec-driven approach: Database → Backend API → Frontend UI → Authentication → Integration Testing → Deployment.

**Primary Requirement**: Create a secure, responsive todo application where users can register, login, and manage their personal tasks through a modern web interface.

**Technical Approach**:
- Monorepo structure with separate frontend (Next.js 16+) and backend (FastAPI) services
- PostgreSQL database with SQLModel ORM for type-safe data access
- Better Auth for JWT-based authentication
- Shadcn/ui components with Framer Motion animations
- **Zustand** for state management (MANDATORY - NO React Context)
- **Axios** for HTTP requests (MANDATORY - NO fetch API)
- Deployment to Vercel with Neon Serverless PostgreSQL

**Core Features**:
1. User Registration & Login (JWT authentication)
2. Create, Read, Update, Delete (CRUD) tasks
3. Toggle task completion
4. User data isolation
5. Responsive mobile-first UI

## Technical Context

**Language/Version**:
| Layer | Technology | Version |
|-------|------------|---------|
| Backend | Python | 3.13+ |
| Backend Package Manager | UV | Latest |
| Frontend | TypeScript | 5.0+ |
| Frontend Runtime | Node.js | 20+ |

**Primary Dependencies**:
**Backend**:
- FastAPI 0.115+
- SQLModel 0.0.24+
- Pydantic 2.0+
- python-jose[cryptography] 3.3.0+ (JWT)
- passlib[bcrypt] 1.7.4+ (Password hashing)
- httpx 0.28.0+ (HTTP client)
- uvicorn[standard] 0.32.0+

**Frontend**:
- Next.js 16+ (App Router)
- React 19
- Shadcn/ui (Radix UI primitives)
- Framer Motion 11+
- Tailwind CSS 4.0
- **Zustand 5.0+** (State Management - MANDATORY)
- **Axios 1.7+** (HTTP Client - MANDATORY)
- Better Auth 1.0+ (JWT Authentication)
- React Hook Form + Zod

**Storage**: Neon Serverless PostgreSQL with async connection pooling via SQLModel

**Testing**:
- Backend: pytest 8.0+, httpx for API tests
- Frontend: Jest + React Testing Library, Playwright for E2E

**Target Platform**:
- Frontend: Vercel Edge Network
- Backend: Vercel Python runtime or Railway
- Database: Neon Serverless (US region)

**Performance Goals**:
| Metric | Target |
|--------|--------|
| API Response Time | < 200ms p95 |
| Page Load Time | < 2s |
| Lighthouse Score | > 85 |
| Database Query Time | < 100ms indexed lookups |
| Concurrent Users | 100 |

**Constraints**:
- Must use spec-driven development (no manual code writing)
- Must pass security checklist (JWT validation, data isolation)
- Must be mobile-responsive (320px+)
- Must deploy to free-tier services

**Scale/Scope**:
- Expected: 100-1000 users
- 10,000 tasks per user maximum
- 7 API endpoints
- 5-8 frontend pages/components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Spec-Driven Development

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Feature specification complete | ✅ | spec.md |
| All user stories have acceptance criteria | ✅ | 8 user stories defined |
| Technical architecture documented | ✅ | System architecture diagram |
| API contracts defined | ✅ | 7 endpoints documented |

### Monorepo Architecture

| Requirement | Status | Evidence |
|-------------|--------|----------|
| `/frontend` and `/backend` directories | ✅ | Monorepo structure |
| `/specs` directory organized by type | ✅ | specs/1-todo-web-app/ |
| Each service has CLAUDE.md | ✅ | Existing CLAUDE.md files |

### Test-First Development

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Test strategy defined | ✅ | pytest + Playwright |
| Acceptance tests before implementation | ✅ | Phase 2C testing phase |
| Test coverage goals: 80% backend, 70% frontend | ✅ | Constitution requirement |

### Authentication & Authorization First

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Better Auth integration planned | ✅ | Constitution Section IV |
| JWT validation strategy defined | ✅ | JWT Bearer token flow |
| User isolation approach documented | ✅ | user_id from JWT filter |
| Secrets management strategy | ✅ | Environment variables |

### API-First Design

| Requirement | Status | Evidence |
|-------------|--------|----------|
| All API endpoints documented | ✅ | 7 endpoints in plan |
| RESTful conventions followed | ✅ | Standard HTTP methods |
| Error response format standardized | ✅ | success/data/error structure |
| HTTP status codes defined | ✅ | 200, 201, 400, 401, 404, 500 |

### Database-First Schema Design

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Complete schema documented | ✅ | users + tasks tables |
| Foreign keys and indexes defined | ✅ | user_id foreign key |
| Migration strategy planned | ✅ | SQLModel auto-migrate |

### Modern UI/UX Standards

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Component library selected | ✅ | Shadcn/ui |
| Animation library chosen | ✅ | Framer Motion |
| State management: Zustand | ✅ | MANDATORY |
| HTTP client: Axios | ✅ | MANDATORY |
| Responsive design | ✅ | Mobile-first approach |
| Dark mode support | ✅ | Constitution requirement |

## Project Structure

### Documentation (this feature)

```text
specs/1-todo-web-app/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (skipped - no clarifications needed)
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── openapi.yaml     # OpenAPI 3.0 specification
│   └── endpoints.json   # Endpoint contracts
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
testing-hackathon2/
├── specs/
│   ├── 1-todo-web-app/
│   │   ├── spec.md
│   │   ├── plan.md
│   │   ├── data-model.md
│   │   ├── quickstart.md
│   │   └── contracts/
│   │       ├── openapi.yaml
│   │       └── endpoints.json
│   └── constitution.md
├── frontend/             # Next.js 16+ application
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── signup/
│   │   │   │       └── page.tsx
│   │   │   └── api/
│   │   ├── components/
│   │   │   ├── ui/           # Shadcn/ui components
│   │   │   ├── auth/         # Auth components
│   │   │   ├── tasks/        # Task components
│   │   │   └── layout/       # Layout components
│   │   ├── stores/           # Zustand stores (MANDATORY)
│   │   │   ├── auth-store.ts
│   │   │   ├── task-store.ts
│   │   │   └── ui-store.ts
│   │   ├── lib/
│   │   │   ├── api.ts        # Axios client
│   │   │   ├── auth.ts       # Better Auth config
│   │   │   ├── types.ts      # TypeScript types
│   │   │   └── utils.ts
│   │   └── styles/
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── next.config.js
│   └── CLAUDE.md
├── backend/              # FastAPI application
│   ├── src/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── db.py
│   │   ├── auth.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── task.py
│   │   │   └── auth.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── tasks.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── task_service.py
│   │   │   └── auth_service.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── jwt_utils.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_tasks.py
│   │   └── integration/
│   │       └── test_full_flow.py
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── CLAUDE.md
├── docker-compose.yml
├── .gitignore
└── CLAUDE.md
```

**Structure Decision**: Monorepo with `/frontend` and `/backend` directories as specified in the constitution. This enables coordinated changes while maintaining clear service boundaries.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | All requirements met without violations | N/A |

## Implementation Phases

### Phase 2A: Foundation & Database (Day 1-2)

**Goal**: Set up project infrastructure and create database schema.

**Tasks**:
1. Initialize UV project in `/backend`
2. Create `pyproject.toml` with dependencies
3. Set up `src/` directory structure
4. Create `main.py` with basic FastAPI app
5. Set up `db.py` with Neon PostgreSQL connection
6. Create SQLModel User and Task models
7. Create Pydantic schemas for validation
8. Test database connection

### Phase 2B: Backend API Development (Day 2-3)

**Goal**: Implement all RESTful API endpoints with JWT authentication.

**Tasks**:
1. Create JWT authentication middleware
2. Implement auth endpoints (register, login)
3. Implement task CRUD endpoints
4. Add error handling
5. Create service layer
6. Document with OpenAPI/Swagger

### Phase 2C: Backend Testing (Day 3)

**Goal**: Write comprehensive tests for all backend functionality.

**Tasks**:
1. Configure pytest fixtures
2. Write authentication tests
3. Write task API tests
4. Write integration tests

### Phase 2D: Frontend Setup (Day 3-4)

**Goal**: Initialize Next.js project with all required dependencies.

**Tasks**:
1. Initialize Next.js 16+ app with TypeScript
2. Install dependencies (Shadcn/ui, Axios, Zustand, Framer Motion, Better Auth)
3. Configure Shadcn/ui components
4. Set up TypeScript types
5. Create Axios API client
6. Create Zustand stores

### Phase 2E: Frontend UI Components (Day 4-5)

**Goal**: Build reusable UI components with animations.

**Tasks**:
1. Create authentication pages
2. Create task components (TaskList, TaskItem, TaskForm)
3. Create layout components
4. Add Framer Motion animations
5. Implement responsive design

### Phase 2F: Frontend Integration (Day 5-6)

**Goal**: Connect frontend to backend API and implement full workflow.

**Tasks**:
1. Wire auth to API
2. Wire tasks to API
3. Implement dashboard
4. Add error handling
5. Polish UI

### Phase 2G: E2E Testing & Polish (Day 6-7)

**Goal**: Write end-to-end tests and finalize for deployment.

**Tasks**:
1. Write Playwright E2E tests
2. Run performance testing
3. Security review
4. Deployment preparation
5. Documentation

## Success Metrics

1. **Functional**:
   - User can register and login
   - User can create, view, edit, delete tasks
   - User can toggle task completion
   - User data is isolated by user_id

2. **Technical**:
   - Next.js 16+ with App Router
   - FastAPI backend with SQLModel
   - Zustand for state management
   - Axios for HTTP requests
   - JWT authentication working

3. **Performance**:
   - Lighthouse score > 85
   - API response time < 200ms
   - Responsive design works on mobile

4. **Quality**:
   - Backend test coverage > 80%
   - Frontend test coverage > 70%
   - All E2E tests passing

---

**Status**: Ready for task breakdown
**Next Command**: `/sp.tasks`
**Est. Completion**: 7 days from start

---

*Generated with Spec-Kit Plus*
*Plan Version*: 1.0.0
*Date*: 2025-12-26

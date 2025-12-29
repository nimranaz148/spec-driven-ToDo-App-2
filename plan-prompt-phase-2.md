# Implementation Plan: Todo Web Application - Phase 2

**Project**: Todo Full-Stack Web Application
**Phase**: Phase 2 - Full-Stack Web Application
**Branch**: `phase-2-web-app`
**Date**: 2025-12-25
**Spec**: [spec-prompt-phase-2.md](./spec-prompt-phase-2.md)
**Constitution**: [constitution-prompt-phase-2.md](./constitution-prompt-phase-2.md)
**Hackathon Requirements**: [Hackathon II - Todo Spec-Driven Development (1).md](./Hackathon%20II%20-%20Todo%20Spec-Driven%20Development%20(1).md)

---

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

**Target Users**: Individual users managing personal todo lists

---

## Performance Goals

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

---

## Technical Context

### Language/Version

| Layer | Technology | Version |
|-------|------------|---------|
| Backend | Python | 3.13+ |
| Backend Package Manager | UV | Latest |
| Frontend | TypeScript | 5.0+ |
| Frontend Runtime | Node.js | 20+ |

### Primary Dependencies

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

### Storage

- **Database**: Neon Serverless PostgreSQL (cloud-hosted)
- **Connection**: Async with connection pooling via SQLModel

### Testing

- Backend: pytest 8.0+, httpx for API tests
- Frontend: Jest + React Testing Library, Playwright for E2E

### Target Platform

- Frontend: Vercel Edge Network
- Backend: Vercel Python runtime or Railway
- Database: Neon Serverless (US region)

---

## Constitution Check

*GATE: Must pass before implementation begins*

### Spec-Driven Development

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Feature specification complete | ✅ | spec-prompt-phase-2.md |
| All user stories have acceptance criteria | ✅ | 8 user stories defined |
| Technical architecture documented | ✅ | System architecture diagram |
| API contracts defined | ✅ | 7 endpoints documented |

### Monorepo Architecture

| Requirement | Status | Evidence |
|-------------|--------|----------|
| `/frontend` and `/backend` directories | 🔄 Pending | Will be created |
| `/specs` directory organized by type | 🔄 Pending | To be structured |
| Each service has CLAUDE.md | ✅ | Existing CLAUDE.md files |

### Test-First Development

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Test strategy defined | ✅ | pytest + Playwright |
| Acceptance tests before implementation | 🔄 Pending | To write in Phase 2A |
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
| All API endpoints documented | ✅ | 7 endpoints in spec |
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

---

## Folder Structure

**Decision**: Chose monorepo structure as per constitution and hackathon requirements.

```
testing-hackathon2/
├── specs/
│   ├── spec-prompt-phase-2.md        # Feature specification
│   ├── constitution-prompt-phase-2.md # Project principles
│   ├── plan-prompt-phase-2.md         # This file
│   ├── overview.md                    # Project overview
│   ├── architecture.md                # System architecture
│   ├── features/
│   │   ├── authentication.md          # Auth feature spec
│   │   └── task-crud.md               # Task CRUD spec
│   ├── api/
│   │   └── endpoints.md               # API documentation
│   ├── database/
│   │   └── schema.md                  # Database schema
│   └── ui/
│       └── components.md              # UI specifications
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx             # Root layout
│   │   │   ├── page.tsx               # Dashboard (protected)
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   │   └── page.tsx       # Login page
│   │   │   │   └── signup/
│   │   │   │       └── page.tsx       # Signup page
│   │   │   └── api/                   # API routes if needed
│   │   ├── components/
│   │   │   ├── ui/                    # Shadcn/ui components
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── checkbox.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   └── label.tsx
│   │   │   ├── auth/
│   │   │   │   ├── auth-form.tsx      # Combined auth form
│   │   │   │   └── protected-route.tsx
│   │   │   ├── tasks/
│   │   │   │   ├── task-list.tsx      # Task list container
│   │   │   │   ├── task-item.tsx      # Individual task
│   │   │   │   ├── task-form.tsx      # Create/edit form
│   │   │   │   └── task-card.tsx      # Card wrapper
│   │   │   └── layout/
│   │   │       ├── header.tsx
│   │   │       └── nav.tsx
│   │   ├── stores/                    # Zustand stores (MANDATORY)
│   │   │   ├── auth-store.ts          # Auth state
│   │   │   ├── task-store.ts          # Task state with optimistic updates
│   │   │   └── ui-store.ts            # UI state
│   │   ├── lib/
│   │   │   ├── api.ts                 # Axios client with interceptors
│   │   │   ├── auth.ts                # Better Auth config
│   │   │   ├── types.ts               # TypeScript types
│   │   │   └── utils.ts               # Utility functions
│   │   └── styles/
│   │       └── globals.css            # Global styles
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.js
│   ├── components.json
│   └── CLAUDE.md
├── backend/
│   ├── src/
│   │   ├── main.py                    # FastAPI app entry
│   │   ├── models.py                  # SQLModel models
│   │   ├── db.py                      # Database connection
│   │   ├── auth.py                    # JWT verification
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── task.py                # Task Pydantic schemas
│   │   │   └── auth.py                # Auth schemas
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                # Auth endpoints
│   │   │   └── tasks.py               # Task endpoints
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── task_service.py        # Task business logic
│   │   │   └── auth_service.py        # Auth business logic
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── jwt_utils.py           # JWT utilities
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py                # Pytest fixtures
│   │   ├── test_auth.py               # Auth tests
│   │   ├── test_tasks.py              # Task API tests
│   │   └── integration/
│   │       └── test_full_flow.py      # E2E tests
│   ├── alembic/                       # Database migrations
│   ├── pyproject.toml                 # UV project config
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── CLAUDE.md
├── .spec-kit/
│   └── config.yaml                    # Spec-Kit configuration
├── docker-compose.yml                 # Local orchestration
├── .gitignore
├── CLAUDE.md                          # Root Claude instructions
└── README.md

**Structure Decision**: Monorepo with `/frontend` and `/backend` directories as specified in the constitution. This enables coordinated changes while maintaining clear service boundaries.

---

## Implementation Phases

### Phase 2A: Foundation & Database (Day 1-2)

**Goal**: Set up project infrastructure and create database schema.

**Tasks**:

1. **Backend Project Setup**
   - Initialize UV project in `/backend`
   - Create `pyproject.toml` with dependencies (FastAPI, SQLModel, Pydantic, JWT, bcrypt)
   - Set up `src/` directory structure
   - Create `main.py` with basic FastAPI app
   - Add CORS configuration
   - Test with `uvicorn main:app --reload`

2. **Database Configuration**
   - Set up `db.py` with Neon PostgreSQL connection
   - Configure async engine with SSL
   - Create session dependency
   - Add startup event for table creation

3. **Database Models**
   - Create `models.py` with SQLModel classes
   - Define `User` model (id, email, name, password_hash, created_at)
   - Define `Task` model (id, user_id, title, description, completed, timestamps)
   - Add relationships (User.tasks → Task.user)
   - Create indexes on user_id, completed
   - Test model creation

4. **Schema Definitions**
   - Create `schemas/task.py` with Pydantic models
   - TaskCreate, TaskUpdate, TaskResponse
   - Create `schemas/auth.py` with auth schemas
   - RegisterRequest, LoginRequest, TokenResponse

**Deliverables**:
- [ ] Backend project structure complete
- [ ] Database connection working
- [ ] SQLModel User and Task models
- [ ] Pydantic schemas for validation
- [ ] Tables created in Neon PostgreSQL

**Tests to Write**:
- Test database connection
- Test model serialization
- Test schema validation

---

### Phase 2B: Backend API Development (Day 2-3)

**Goal**: Implement all RESTful API endpoints with JWT authentication.

**Tasks**:

1. **JWT Authentication**
   - Create `auth.py` middleware
   - Implement `get_current_user` dependency
   - Extract JWT from Authorization header
   - Verify token using BETTER_AUTH_SECRET
   - Return 401 for invalid/expired tokens

2. **Auth Endpoints**
   - Create `routes/auth.py`
   - POST `/api/auth/register` - Create user, hash password with bcrypt
   - POST `/api/auth/login` - Validate credentials, return JWT token
   - Add rate limiting (optional)

3. **Task Endpoints**
   - Create `routes/tasks.py`
   - GET `/api/{user_id}/tasks` - List all user tasks (sorted by created_at desc)
   - POST `/api/{user_id}/tasks` - Create new task
   - GET `/api/{user_id}/tasks/{id}` - Get single task
   - PUT `/api/{user_id}/tasks/{id}` - Update task
   - DELETE `/api/{user_id}/tasks/{id}` - Delete task
   - PATCH `/api/{user_id}/tasks/{id}/complete` - Toggle completion

4. **Error Handling**
   - Create standardized error response format
   - Handle 401 Unauthorized
   - Handle 404 Not Found (task not found)
   - Handle 400 Bad Request (validation errors)
   - Handle 500 Internal Server Error

5. **Service Layer**
   - Create `services/task_service.py`
   - Extract business logic from routes
   - Add user_id filter to all queries
   - Implement optimistic locking (optional)

**Deliverables**:
- [ ] JWT authentication working
- [ ] All 7 API endpoints implemented
- [ ] User data isolation enforced
- [ ] Error handling standardized
- [ ] API documentation with OpenAPI/Swagger

**Tests to Write**:
- Test JWT token generation and validation
- Test auth endpoints (register, login)
- Test task CRUD endpoints
- Test user isolation (cannot access other user's tasks)
- Test error responses

---

### Phase 2C: Backend Testing (Day 3)

**Goal**: Write comprehensive tests for all backend functionality.

**Tasks**:

1. **Pytest Setup**
   - Configure `conftest.py`
   - Create test fixtures (test client, test database, sample data)
   - Set up test database (use test URL or mock)

2. **Authentication Tests**
   - Test user registration
   - Test login with valid credentials
   - Test login with invalid credentials
   - Test JWT token expiration
   - Test JWT token with invalid signature

3. **Task API Tests**
   - Test create task
   - Test list tasks (empty and with data)
   - Test get single task
   - Test update task
   - Test delete task
   - Test toggle completion
   - Test user isolation

4. **Integration Tests**
   - Test full user workflow (register → login → CRUD)
   - Test concurrent requests (optional)

**Deliverables**:
- [ ] Test suite with 80%+ coverage
- [ ] All critical paths tested
- [ ] Tests pass locally
- [ ] CI/CD pipeline configured (optional)

---

### Phase 2D: Frontend Setup (Day 3-4)

**Goal**: Initialize Next.js project with all required dependencies.

**Tasks**:

1. **Initialize Next.js Project**
   - Create Next.js 16+ app with TypeScript
   - Configure App Router
   - Set up Tailwind CSS

2. **Install Dependencies**
   - Install Shadcn/ui CLI and base components
   - Install Axios (MANDATORY)
   - Install Zustand (MANDATORY)
   - Install Framer Motion
   - Install Better Auth
   - Install React Hook Form + Zod

3. **Configure Shadcn/ui**
   - Initialize shadcn-ui
   - Add components: Button, Card, Input, Checkbox, Dialog, Label
   - Configure tailwind.config.ts

4. **Set Up TypeScript**
   - Create `lib/types.ts`
   - Define Task, User interfaces
   - Configure strict mode

5. **Create API Client**
   - Create `lib/api.ts` with Axios instance
   - Add request interceptor for JWT token
   - Add response interceptor for error handling
   - Create API helper functions

6. **Create Zustand Stores**
   - Create `stores/auth-store.ts` with persist middleware
   - Create `stores/task-store.ts` with optimistic updates
   - Create `stores/ui-store.ts` for modals/theme

**Deliverables**:
- [ ] Next.js project initialized
- [ ] All dependencies installed
- [ ] Shadcn/ui components configured
- [ ] Axios client configured with interceptors
- [ ] Zustand stores created
- [ ] TypeScript types defined

---

### Phase 2E: Frontend UI Components (Day 4-5)

**Goal**: Build reusable UI components with animations.

**Tasks**:

1. **Authentication Components**
   - Create Login page with form
   - Create Signup page with form
   - Add form validation with Zod
   - Show loading states
   - Handle errors gracefully

2. **Task Components**
   - Create TaskList component
   - Create TaskItem component (with checkbox + edit/delete buttons)
   - Create TaskForm component (create + edit mode)
   - Create EmptyState component
   - Add Skeleton loading states

3. **Layout Components**
   - Create Header with user info and logout
   - Create responsive navigation
   - Create main dashboard layout

4. **Add Animations**
   - Add Framer Motion to TaskItem (entry/exit)
   - Add page transitions
   - Add hover effects and micro-interactions
   - Animate task creation/deletion

5. **Responsive Design**
   - Test on mobile (320px+)
   - Test on tablet
   - Test on desktop
   - Ensure touch-friendly targets

**Deliverables**:
- [ ] Login and Signup pages working
- [ ] All task components implemented
- [ ] Layout with header and navigation
- [ ] Framer Motion animations
- [ ] Fully responsive (mobile, tablet, desktop)
- [ ] Dark mode supported

---

### Phase 2F: Frontend Integration (Day 5-6)

**Goal**: Connect frontend to backend API and implement full workflow.

**Tasks**:

1. **Connect Auth to API**
   - Wire login form to auth API
   - Wire signup form to auth API
   - Store JWT in Zustand persist store
   - Implement protected route middleware
   - Implement logout functionality

2. **Connect Tasks to API**
   - Wire TaskList to task API
   - Wire TaskForm create to API
   - Wire TaskItem actions to API
   - Implement optimistic updates in Zustand
   - Handle rollback on errors

3. **Implement Dashboard**
   - Create main dashboard page
   - Show task list with filters (all/active/completed)
   - Show task count summary
   - Add "Add Task" button
   - Implement edit mode

4. **Error Handling**
   - Show toast notifications for errors
   - Handle 401 (redirect to login)
   - Handle 404 (task not found)
   - Handle network errors
   - Show loading states

5. **Polish UI**
   - Add empty states
   - Add confirmations for destructive actions
   - Add keyboard shortcuts (Enter to submit)
   - Add focus management

**Deliverables**:
- [ ] Full authentication flow working
- [ ] Task CRUD working from UI
- [ ] Optimistic updates implemented
- [ ] Error handling complete
- [ ] Dashboard fully functional

---

### Phase 2G: E2E Testing & Polish (Day 6-7)

**Goal**: Write end-to-end tests and finalize for deployment.

**Tasks**:

1. **Playwright E2E Tests**
   - Test user registration flow
   - Test login/logout flow
   - Test create task
   - Test toggle completion
   - Test edit task
   - Test delete task
   - Test user isolation (different browser)

2. **Performance Testing**
   - Run Lighthouse audit
   - Optimize images (if any)
   - Minimize bundle size
   - Test on slow network (3G)

3. **Security Review**
   - Verify JWT validation on all endpoints
   - Verify user data isolation
   - Check environment variables
   - Verify no secrets in code

4. **Deployment Preparation**
   - Create production build
   - Test locally with production build
   - Prepare environment variables
   - Create deployment documentation

5. **Documentation**
   - Update README.md with setup instructions
   - Document API endpoints
   - Add screenshots (optional)

**Deliverables**:
- [ ] E2E tests passing
- [ ] Lighthouse score > 85
- [ ] Security checklist complete
- [ ] Deployment ready
- [ ] README updated

---

## Risk Management

| Risk | Impact | Mitigation |
|------|--------|------------|
| Database connection issues | High | Use connection pooling, handle disconnects |
| JWT token expiration | Medium | Implement refresh token flow (Phase 3) |
| CORS errors | Medium | Configure CORS properly for all origins |
| TypeScript errors | Low | Enable strict mode, use IDE |
| Performance issues | Medium | Implement pagination, optimize queries |
| Cross-browser compatibility | Low | Test on multiple browsers early |

---

## Timeline Estimate

**Total Duration**: 7 days

| Phase | Duration | Focus |
|-------|----------|-------|
| Phase 2A: Foundation & Database | Day 1-2 | Backend setup, DB models |
| Phase 2B: Backend API | Day 2-3 | API endpoints, JWT auth |
| Phase 2C: Backend Testing | Day 3 | pytest suite |
| Phase 2D: Frontend Setup | Day 3-4 | Next.js, dependencies |
| Phase 2E: UI Components | Day 4-5 | Components, animations |
| Phase 2F: Frontend Integration | Day 5-6 | Connect to API |
| Phase 2G: E2E & Polish | Day 6-7 | Testing, deployment |

---

## Success Metrics

Phase 2 is successful when:

1. **Functional**:
   - [ ] User can register and login
   - [ ] User can create, view, edit, delete tasks
   - [ ] User can toggle task completion
   - [ ] User data is isolated by user_id

2. **Technical**:
   - [ ] Next.js 16+ with App Router
   - [ ] FastAPI backend with SQLModel
   - [ ] Zustand for state management
   - [ ] Axios for HTTP requests
   - [ ] JWT authentication working

3. **Performance**:
   - [ ] Lighthouse score > 85
   - [ ] API response time < 200ms
   - [ ] Responsive design works on mobile

4. **Quality**:
   - [ ] Backend test coverage > 80%
   - [ ] Frontend test coverage > 70%
   - [ ] All E2E tests passing

5. **Documentation**:
   - [ ] README includes setup instructions
   - [ ] API endpoints documented
   - [ ] PHR created for major decisions

---

## Next Steps

1. **Run `/sp.tasks`** to generate detailed task breakdown from this plan
2. **Run `/sp.implement`** to begin execution of tasks
3. **Create PHR** after each major milestone
4. **Consider ADR** for significant architectural decisions

---

## References

- [Phase 2 Specification](./spec-prompt-phase-2.md)
- [Phase 2 Constitution](./constitution-prompt-phase-2.md)
- [Hackathon II Requirements](./Hackathon%20II%20-%20Todo%20Spec-Driven%20Development%20(1).md)
- [Root CLAUDE.md](../CLAUDE.md)
- [Frontend CLAUDE.md](../frontend/CLAUDE.md)
- [Backend CLAUDE.md](../backend/CLAUDE.md)

**Spec-Kit Integration**:
- Use `@sp.specify` to update feature specs
- Use `@sp.plan` to regenerate this plan
- Use `@sp.tasks` to generate task breakdown
- Use `@sp.implement` to execute tasks

---

**Status**: Ready for task breakdown
**Next Command**: `/sp.tasks`
**Est. Completion**: 7 days from start

---

*Generated with Spec-Kit Plus*
*Plan Version*: 1.0.0
*Date*: 2025-12-25

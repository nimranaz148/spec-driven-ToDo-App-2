# Tasks: Todo Web Application - Phase 2

**Feature**: Todo Full-Stack Web Application
**Version**: 1.0.0
**Date**: 2025-12-26
**Input**: Design documents from `/specs/1-todo-web-app/`

**Tests**: Test tasks included per Constitution requirement (80% backend, 70% frontend coverage)

**Organization**: Tasks grouped by user story to enable independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, etc.)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for both frontend and backend

- [X] T001 Create project structure per plan.md: `frontend/` and `backend/` directories
- [X] T002 [P] Initialize backend UV project with pyproject.toml in `backend/pyproject.toml`
- [X] T003 [P] Initialize frontend Next.js 16+ project with TypeScript in `frontend/`
- [X] T004 [P] Install backend dependencies: FastAPI, SQLModel, Pydantic, python-jose, passlib, httpx, uvicorn
- [X] T005 [P] Install frontend dependencies: Shadcn/ui, Axios, Zustand, Framer Motion, Better Auth, React Hook Form, Zod
- [X] T006 Configure backend CORS for frontend origin in `backend/src/main.py`
- [X] T007 Configure TypeScript strict mode and paths in `frontend/tsconfig.json`
- [X] T008 Create environment variable templates: `backend/.env.example` and `frontend/.env.example`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [X] T009 Setup database connection in `backend/src/db.py` for Neon PostgreSQL
- [X] T010 [P] Create SQLModel User model in `backend/src/models.py`
- [X] T011 [P] Create SQLModel Task model in `backend/src/models.py`
- [X] T012 [P] Create Pydantic auth schemas in `backend/src/schemas/auth.py`
- [X] T013 [P] Create Pydantic task schemas in `backend/src/schemas/task.py`
- [X] T014 Implement JWT authentication middleware in `backend/src/auth.py`
- [X] T015 Create JWT utilities in `backend/src/utils/jwt_utils.py`
- [X] T016 [P] Setup FastAPI app with OpenAPI in `backend/src/main.py`
- [X] T017 [P] Configure database session dependency in `backend/src/main.py`

### Rate Limiting

- [X] T018-RL [P] Implement rate limiting middleware (60 req/min per user) in `backend/src/middleware/rate_limit.py`
- [X] T019-RL [P] Add rate limit headers to responses in `backend/src/middleware/rate_limit.py`
- [X] T020-RL Test rate limiting in `backend/tests/test_rate_limit.py`

### Frontend Foundation

- [X] T018 [P] Configure Shadcn/ui components: Button, Card, Input, Checkbox, Dialog, Label
- [X] T019 [P] Create TypeScript interfaces in `frontend/src/lib/types.ts`
- [X] T020 Create Axios API client with interceptors in `frontend/src/lib/api.ts`
- [X] T021 [P] Create Zustand auth store in `frontend/src/stores/auth-store.ts`
- [X] T022 [P] Create Zustand task store in `frontend/src/stores/task-store.ts`
- [X] T023 [P] Create Zustand UI store in `frontend/src/stores/ui-store.ts`
- [X] T024 Configure Better Auth JWT plugin in `frontend/src/lib/auth.ts`
- [X] T025 Setup global styles in `frontend/src/styles/globals.css`

### Backend Tests - Foundational

- [X] T026 Configure pytest fixtures in `backend/tests/conftest.py`
- [X] T027 [P] Write test for database connection in `backend/tests/test_db.py`
- [X] T028 [P] Write test for User model serialization in `backend/tests/test_models.py`
- [X] T029 [P] Write test for JWT token generation in `backend/tests/test_jwt.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration & Login (Priority: P1) 🎯 MVP

**Goal**: Users can register and login to receive JWT tokens for authentication

**Independent Test**: User can register, then login with same credentials, and receive valid JWT token

### Backend Tests - US1

- [X] T030 [P] [US1] Contract test for POST /api/auth/register in `backend/tests/test_auth.py`
- [X] T031 [P] [US1] Contract test for POST /api/auth/login in `backend/tests/test_auth.py`
- [X] T032 [US1] Integration test for full auth flow in `backend/tests/integration/test_auth_flow.py`

### Backend Implementation - US1

- [X] T033 [US1] Implement password hashing utility in `backend/src/utils/password.py`
- [X] T034 [US1] Implement user service for registration in `backend/src/services/auth_service.py`
- [X] T035 [US1] Implement login validation in `backend/src/services/auth_service.py`
- [X] T036 [US1] Create auth routes in `backend/src/routes/auth.py`
- [X] T037 [US1] Add input validation with Pydantic in `backend/src/routes/auth.py`
- [X] T038 [US1] Add proper error responses for auth endpoints in `backend/src/routes/auth.py`

### Frontend Implementation - US1

- [X] T039 [P] [US1] Create login page component in `frontend/src/app/(auth)/login/page.tsx`
- [X] T040 [P] [US1] Create signup page component in `frontend/src/app/(auth)/signup/page.tsx`
- [X] T041 [US1] Create auth form component in `frontend/src/components/auth/auth-form.tsx`
- [X] T042 [US1] Wire login form to auth API in `frontend/src/components/auth/auth-form.tsx`
- [X] T043 [US1] Wire signup form to auth API in `frontend/src/components/auth/auth-form.tsx`
- [X] T044 [US1] Store JWT in Zustand persist store in `frontend/src/stores/auth-store.ts`
- [X] T045 [US1] Implement protected route middleware in `frontend/src/components/auth/protected-route.tsx`

### Frontend Tests - US1

- [X] T046 [P] [US1] Test login form validation in `frontend/tests/auth/login.test.tsx`
- [X] T047 [P] [US1] Test signup form validation in `frontend/tests/auth/signup.test.tsx`

**Checkpoint**: User Story 1 complete - users can register, login, and maintain authenticated state

---

## Phase 4: User Story 2 - Task CRUD Operations (Priority: P1) 🎯 MVP

**Goal**: Users can create, read, update, and delete their own tasks

**Independent Test**: User can create a task, view it, edit it, and delete it through the UI

### Backend Tests - US2

- [X] T048 [P] [US2] Contract test for GET /api/{user_id}/tasks in `backend/tests/test_tasks.py`
- [X] T049 [P] [US2] Contract test for POST /api/{user_id}/tasks in `backend/tests/test_tasks.py`
- [X] T050 [P] [US2] Contract test for PUT /api/{user_id}/tasks/{id} in `backend/tests/test_tasks.py`
- [X] T051 [P] [US2] Contract test for DELETE /api/{user_id}/tasks/{id} in `backend/tests/test_tasks.py`
- [X] T052 [US2] Integration test for full task CRUD flow in `backend/tests/integration/test_task_crud.py`

### Backend Implementation - US2

- [X] T053 [US2] Implement task service in `backend/src/services/task_service.py`
- [X] T054 [US2] Create task routes with user_id filtering in `backend/src/routes/tasks.py`
- [X] T055 [US2] Implement GET endpoint for listing tasks in `backend/src/routes/tasks.py`
- [X] T056 [US2] Implement POST endpoint for creating tasks in `backend/src/routes/tasks.py`
- [X] T057 [US2] Implement PUT endpoint for updating tasks in `backend/src/routes/tasks.py`
- [X] T058 [US2] Implement DELETE endpoint for removing tasks in `backend/src/routes/tasks.py`
- [X] T059 [US2] Add error handling for task not found in `backend/src/routes/tasks.py`

### Frontend Implementation - US2

- [X] T060 [P] [US2] Create task list component in `frontend/src/components/tasks/task-list.tsx`
- [X] T061 [P] [US2] Create task item component in `frontend/src/components/tasks/task-item.tsx`
- [X] T062 [P] [US2] Create task card wrapper in `frontend/src/components/tasks/task-card.tsx`
- [X] T063 [US2] Create task form component in `frontend/src/components/tasks/task-form.tsx`
- [X] T064 [US2] Wire TaskList to task API in `frontend/src/components/tasks/task-list.tsx`
- [X] T065 [US2] Wire TaskForm create to API in `frontend/src/components/tasks/task-form.tsx`
- [X] T066 [US2] Wire TaskItem actions to API in `frontend/src/components/tasks/task-item.tsx`
- [X] T067 [US2] Implement optimistic updates in `frontend/src/stores/task-store.ts`

### Frontend Tests - US2

- [X] T068 [P] [US2] Test TaskList component in `frontend/tests/tasks/task-list.test.tsx`
- [X] T069 [P] [US2] Test TaskForm component in `frontend/tests/tasks/task-form.test.tsx`

**Checkpoint**: User Story 2 complete - users can perform full CRUD on their tasks

---

## Phase 5: User Story 3 - User Logout (Priority: P1) 🎯 MVP

**Goal**: Users can securely log out and terminate their session

**Independent Test**: User clicks logout, JWT is invalidated, and user is redirected to login page

### Backend Tests - US3

- [X] T048-US3 [P] [US3] Contract test for POST /api/auth/logout in `backend/tests/test_auth.py`
- [X] T049-US3 [US3] Integration test for logout flow in `backend/tests/integration/test_logout.py`

### Backend Implementation - US3

- [X] T050-US3 [US3] Implement logout endpoint in `backend/src/routes/auth.py`
- [X] T051-US3 [US3] Add token invalidation to JWT utilities in `backend/src/utils/jwt_utils.py`
- [X] T052-US3 [US3] Add logout to auth service in `backend/src/services/auth_service.py`

### Frontend Implementation - US3

- [X] T053-US3 [P] [US3] Add logout button to header component in `frontend/src/components/layout/header.tsx`
- [X] T054-US3 [US3] Implement logout handler in `frontend/src/components/layout/header.tsx`
- [X] T055-US3 [US3] Clear JWT from Zustand auth store in `frontend/src/stores/auth-store.ts`
- [X] T056-US3 [US3] Redirect to login page after logout in `frontend/src/components/layout/header.tsx`

### Frontend Tests - US3

- [X] T057-US3 [US3] Test logout button in `frontend/tests/auth/logout.test.tsx`

**Checkpoint**: User Story 3 complete - users can securely log out

---

## Phase 6: User Story 4 - Toggle Task Completion (Priority: P2)

**Goal**: Users can mark tasks as complete/incomplete with visual feedback

**Independent Test**: User can click checkbox on task to toggle completion status

### Backend Tests - US4

- [X] T070 [P] [US4] Contract test for PATCH /api/{user_id}/tasks/{id}/complete in `backend/tests/test_tasks.py`

### Backend Implementation - US4

- [X] T071 [US4] Implement toggle completion endpoint in `backend/src/routes/tasks.py`

### Frontend Implementation - US4

- [X] T072 [P] [US4] Add checkbox component for task completion in `frontend/src/components/tasks/task-item.tsx`
- [X] T073 [US4] Wire toggle completion to API in `frontend/src/components/tasks/task-item.tsx`
- [X] T074 [US4] Add completion visual styling in `frontend/src/components/tasks/task-item.tsx`

### Frontend Tests - US4

- [X] T075 [US4] Test task completion toggle in `frontend/tests/tasks/task-item.test.tsx`

**Checkpoint**: User Story 4 complete - tasks can be toggled complete/incomplete

---

## Phase 7: User Story 5 - User Data Isolation (Priority: P1) 🎯 MVP

**Goal**: Users can only access their own tasks; data isolation enforced at API level

**Independent Test**: User A cannot see User B's tasks even with valid JWT

### Backend Tests - US5

- [X] T076 [US5] Test user isolation in `backend/tests/test_user_isolation.py`

### Backend Implementation - US5

- [X] T077 [US5] Enforce user_id from JWT on all task queries in `backend/src/routes/tasks.py`
- [X] T078 [US5] Add 404 response when task not found or belongs to another user in `backend/src/routes/tasks.py`

**Checkpoint**: User Story 5 complete - users cannot access other users' data

---

## Phase 8: User Story 6 - Responsive UI & Polish (Priority: P2)

**Goal**: Mobile-first responsive design with smooth animations

**Independent Test**: Application works on mobile (320px+) and desktop, animations are smooth

### Frontend Implementation - US6

- [X] T079 [P] [US6] Create responsive layout in `frontend/src/components/layout/header.tsx`
- [X] T080 [P] [US6] Create navigation component in `frontend/src/components/layout/nav.tsx`
- [X] T081 [US6] Add Framer Motion animations to TaskItem in `frontend/src/components/tasks/task-item.tsx`
- [X] T082 [US6] Add page transitions in `frontend/src/app/layout.tsx`
- [X] T083 [US6] Ensure touch-friendly targets (min 44px) in all interactive components
- [X] T084 [US6] Implement dark mode support in `frontend/src/styles/globals.css`
- [X] T085 [US6] Create empty state component in `frontend/src/components/tasks/empty-state.tsx`
- [X] T086 [US6] Add skeleton loading states in `frontend/src/components/tasks/skeleton.tsx`

### Frontend Tests - US6

- [X] T087 [US6] Test responsive layout in `frontend/tests/layout/responsive.test.tsx`
- [X] T088 [US6] Test dark mode toggle in `frontend/tests/ui/dark-mode.test.tsx`

### Accessibility (WCAG 2.1 AA)

- [X] T089-ACC [P] [US6] Add keyboard navigation support in all interactive components
- [X] T090-ACC [P] [US6] Ensure 4.5:1 contrast ratio for text in `frontend/src/styles/globals.css`
- [X] T091-ACC [US6] Add ARIA labels to all interactive elements in `frontend/src/components/`
- [X] T092-ACC [US6] Add focus management for forms and modals in `frontend/src/components/`
- [X] T093-ACC [US6] Test with screen reader (NVDA/VoiceOver) in `frontend/tests/a11y/`
- [X] T094-ACC [US6] Ensure minimum touch target size 44px in all interactive components

**Checkpoint**: User Story 6 complete - UI is responsive, animated, and accessible

---

## Phase 9: Integration & E2E Testing

**Purpose**: Verify full user workflows and end-to-end functionality

### Backend Integration Tests

- [X] T089 Full user workflow test: register → login → CRUD in `backend/tests/integration/test_full_flow.py`
- [X] T090 Test concurrent requests in `backend/tests/integration/test_concurrent.py`

### Frontend E2E Tests

- [ ] T091 [P] E2E test for user registration flow in `frontend/tests/e2e/register.spec.ts`
- [ ] T092 [P] E2E test for login/logout flow in `frontend/tests/e2e/login.spec.ts`
- [ ] T093 [P] E2E test for create task in `frontend/tests/e2e/create-task.spec.ts`
- [ ] T094 [P] E2E test for complete task in `frontend/tests/e2e/complete-task.spec.ts`
- [ ] T095 [P] E2E test for delete task in `frontend/tests/e2e/delete-task.spec.ts`

### Performance Tests

- [ ] T096 Run Lighthouse audit targeting score > 85
- [ ] T097 Test API response time < 200ms p95
- [ ] T098 Test on slow network (3G)

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Observability & Logging

- [X] T105-OBS [P] Implement structured JSON logging in `backend/src/utils/logger.py`
- [X] T106-OBS [P] Add request ID middleware for tracing in `backend/src/middleware/request_id.py`
- [X] T107-OBS Log all authentication attempts (success/failure) in `backend/src/routes/auth.py`
- [X] T108-OBS Log all database errors in `backend/src/db.py`
- [X] T109-OBS Add API response time metrics in `backend/src/middleware/timing.py`
- [X] T110-OBS Never log sensitive data (passwords, tokens, JWTs) - verify in code review

### General Polish

- [X] T099 [P] Update README.md with setup instructions
- [X] T100 [P] Document API endpoints in `docs/api.md`
- [X] T101 Code cleanup and refactoring across codebase
- [X] T102 [P] Security hardening review
- [X] T103 [P] Environment variables validation
- [X] T104 Run quickstart.md validation
- [X] T111 Deploy preparation and documentation

---

## Dependencies & Execution Order

### Phase Dependencies

| Phase | Depends On | Blocks |
|-------|------------|--------|
| Phase 1: Setup | None | Phase 2 |
| Phase 2: Foundational | Phase 1 | All User Stories |
| Phase 3: US1 (Auth) | Phase 2 | None (MVP) |
| Phase 4: US2 (CRUD) | Phase 2 | None (MVP) |
| Phase 5: US3 (Logout) | Phase 2 | None (MVP) |
| Phase 6: US4 (Toggle) | Phase 2 | None |
| Phase 7: US5 (Isolation) | Phase 2 | None (MVP) |
| Phase 8: US6 (UI) | Phase 4 | None |
| Phase 9: Integration | All User Stories | None |
| Phase 10: Polish | All Phases | None |

### User Story Dependencies

| Story | Priority | Can Start After | Dependencies |
|-------|----------|-----------------|--------------|
| US1: Auth | P1 | Phase 2 | None |
| US2: CRUD | P1 | Phase 2 | None (depends on US1 implicitly for auth) |
| US3: Logout | P1 | Phase 2 | None |
| US4: Toggle | P2 | Phase 2 | None |
| US5: Isolation | P1 | Phase 2 | None |
| US6: UI | P2 | Phase 4 | US2 components |

### Within Each User Story

1. Tests (if included) MUST be written and FAIL before implementation
2. Models before services
3. Services before endpoints
4. Core implementation before integration
5. Story complete before moving to next priority

### Parallel Opportunities

- Phase 1: T002-T005 can run in parallel (different projects)
- Phase 2: T010-T017 can run in parallel (different backend files), T018-T025 can run in parallel (different frontend files)
- Phase 3+: Once Foundation is done, US1-US5 can proceed in parallel (different developers)
- Within US: Models and schemas marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: T030 - Contract test for POST /api/auth/register
Task: T031 - Contract test for POST /api/auth/login
Task: T032 - Integration test for auth flow

# Launch all models for User Story 1 together:
Task: T033 - Password hashing utility
Task: T034 - User service for registration
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Auth)
4. Complete Phase 4: User Story 2 (CRUD)
5. Complete Phase 5: User Story 3 (Logout)
6. Complete Phase 7: User Story 5 (Isolation)
7. **STOP and VALIDATE**: Test MVP independently
8. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US1 → Test → Deploy/Demo (Auth MVP!)
3. Add US2 → Test → Deploy/Demo (CRUD MVP!)
4. Add US3 → Test → Deploy/Demo (Logout!)
5. Add US5 → Test → Deploy/Demo (Secure MVP!)
6. Add US4 → Test → Deploy/Demo (Toggle feature)
7. Add US6 → Test → Deploy/Demo (Polished UI)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Auth)
   - Developer B: User Story 2 (CRUD)
   - Developer C: User Story 3 (Logout) / User Story 5 (Isolation)
3. Stories complete and integrate independently

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 130 |
| Setup Tasks | 8 |
| Foundational Tasks (incl. rate limiting) | 24 |
| User Story Tasks | 71 |
| Integration Tasks | 11 |
| Polish Tasks (incl. observability) | 14 |
| Backend Tests | 15 |
| Frontend Tests | 13 |
| E2E Tests | 5 |
| Accessibility Tasks | 6 |

### Parallel Opportunities

- All Setup tasks (T001-T008) can start immediately
- Foundational tasks split by backend/frontend, can run in parallel
- User stories can run in parallel after Foundation (US1-US5)
- US6 depends on US2 for components

### MVP Scope

MVP = Phase 1 + Phase 2 + Phase 3 (US1) + Phase 4 (US2) + Phase 5 (US3) + Phase 7 (US5)
- User can: Register, Login, Logout, Create/View/Edit/Delete tasks, Data isolated
- Excluded from MVP: Toggle completion, Polish UI, Accessibility

---

*Generated with Spec-Kit Plus*
*Version*: 1.0.0
*Date*: 2025-12-26

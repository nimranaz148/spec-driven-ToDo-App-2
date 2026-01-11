# Todo App - Phase 2 Specification

**Project**: Todo Full-Stack Web Application
**Phase**: Phase 2 - Full-Stack Web Application
**Version**: 2.0.0
**Created**: 2025-12-25
**Status**: Ready for Specification
**Priority**: P1 (Critical)

---

## Overview

This specification defines the requirements, architecture, and implementation details for Phase 2 of the Todo App project. Phase 2 transforms the Phase 1 console application into a production-ready, multi-user web application with persistent storage.

**Reference Documents**:
- Constitution: `constitution-prompt-phase-2.md`
- Hackathon Requirements: `Hackathon II - Todo Spec-Driven Development (1).md`
- Root CLAUDE.md: `@CLAUDE.md`
- Frontend Guidelines: `@frontend/CLAUDE.md`
- Backend Guidelines: `@backend/CLAUDE.md`

---

## 1. Project Scope

### 1.1 In Scope

- User authentication with email/password
- JWT token-based authentication
- RESTful API for task management
- React frontend with Next.js 16+
- PostgreSQL database with SQLModel
- Responsive UI with Tailwind CSS
- Task CRUD operations (Create, Read, Update, Delete)
- Mark tasks as complete/incomplete
- User data isolation

### 1.2 Out of Scope

- AI Chatbot interface (Phase 3)
- Task priorities and tags (Phase 5)
- Due dates and reminders (Phase 5)
- Recurring tasks (Phase 5)
- Search and filtering (Phase 5)
- Voice commands (Bonus)

---

## 2. User Stories

### US-001: User Registration
**Priority**: P1
**As a** new user,
**I want** to create an account with email and password,
**So that** I can securely access my personal todo list.

**Acceptance Criteria**:
- User can register with valid email and password (min 8 characters)
- Email format is validated before submission
- Password strength requirements are enforced
- Account is created and user is logged in automatically
- User cannot register with duplicate email

### US-002: User Login
**Priority**: P1
**As a** registered user,
**I want** to log in with my email and password,
**So that** I can access my todo list.

**Acceptance Criteria**:
- User can login with registered email/password
- JWT token is issued upon successful login
- User is redirected to dashboard after login
- Invalid credentials show appropriate error message
- Session persists across browser refresh

### US-003: User Logout
**Priority**: P1
**As a** logged-in user,
**I want** to log out of my account,
**So that** my session is terminated securely.

**Acceptance Criteria**:
- User can click logout button to end session
- JWT token is cleared from client
- User is redirected to login page
- User cannot access protected routes after logout

### US-004: View Tasks
**Priority**: P1
**As a** logged-in user,
**I want** to see all my tasks in a clean list,
**So that** I can understand what I need to do.

**Acceptance Criteria**:
- All tasks belonging to the user are displayed
- Tasks are sorted by creation date (newest first)
- Completed tasks show visual distinction
- Empty state is shown when no tasks exist
- Task count summary is displayed

### US-005: Create Task
**Priority**: P1
**As a** logged-in user,
**I want** to add a new task with title and optional description,
**So that** I can capture my todos.

**Acceptance Criteria**:
- Task can be created with title (required, 1-200 chars)
- Optional description can be added (max 1000 chars)
- New task appears at the top of the list
- Optimistic UI update on creation
- Validation errors show for invalid input

### US-006: Toggle Task Completion
**Priority**: P1
**As a** logged-in user,
**I want** to mark tasks as complete or incomplete,
**So that** I can track my progress.

**Acceptance Criteria**:
- Clicking checkbox toggles task completion status
- Visual feedback (strikethrough, color change) on completion
- Toggle updates are persisted to database
- Completed tasks can be toggled back to incomplete

### US-007: Edit Task
**Priority**: P2
**As a** logged-in user,
**I want** to edit an existing task's title and description,
**So that** I can correct or update my tasks.

**Acceptance Criteria**:
- Task title and description can be edited
- Edit mode is triggered by clicking edit button
- Changes are saved on submit
- Cancel button discards changes
- Validation applies to edited fields

### US-008: Delete Task
**Priority**: P2
**As a** logged-in user,
**I want** to permanently delete a task,
**So that** I can remove unwanted tasks.

**Acceptance Criteria**:
- Task can be deleted by clicking delete button
- Confirmation dialog appears before deletion
- Deleted task is removed from the list
- Deletion is persisted to database

---

## 3. Functional Requirements

### 3.1 Authentication (FR-AUTH)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-AUTH-001 | System MUST allow new users to register with email and password | P1 |
| FR-AUTH-002 | System MUST validate email format | P1 |
| FR-AUTH-003 | System MUST validate password (min 8 characters) | P1 |
| FR-AUTH-004 | System MUST issue JWT tokens upon successful authentication | P1 |
| FR-AUTH-005 | System MUST validate JWT tokens on all protected API endpoints | P1 |
| FR-AUTH-006 | System MUST enforce user isolation - users only access their own data | P1 |
| FR-AUTH-007 | System MUST hash passwords with bcrypt | P1 |
| FR-AUTH-008 | System MUST support user logout | P1 |

### 3.2 Task Management (FR-TASK)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-TASK-001 | System MUST allow authenticated users to create tasks | P1 |
| FR-TASK-002 | System MUST persist all tasks to PostgreSQL database | P1 |
| FR-TASK-003 | System MUST allow users to view all their tasks | P1 |
| FR-TASK-004 | System MUST allow users to mark tasks as complete/incomplete | P1 |
| FR-TASK-005 | System MUST allow users to edit task title and description | P2 |
| FR-TASK-006 | System MUST allow users to delete tasks | P2 |
| FR-TASK-007 | System MUST validate task title (1-200 characters) | P1 |
| FR-TASK-008 | System MUST validate task description (max 1000 characters) | P1 |
| FR-TASK-009 | System MUST automatically timestamp tasks | P1 |
| FR-TASK-010 | System MUST return tasks sorted by creation date (newest first) | P1 |

### 3.3 API Requirements (FR-API)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-API-001 | System MUST expose RESTful API endpoints | P1 |
| FR-API-002 | System MUST return appropriate HTTP status codes | P1 |
| FR-API-003 | System MUST return consistent JSON response format | P1 |
| FR-API-004 | System MUST validate input data with Pydantic schemas | P1 |
| FR-API-005 | System MUST include CORS headers for frontend | P1 |

### 3.4 UI Requirements (FR-UI)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-UI-001 | System MUST provide responsive UI for mobile and desktop | P1 |
| FR-UI-002 | System MUST support dark mode | P1 |
| FR-UI-003 | System MUST show loading states for async operations | P1 |
| FR-UI-004 | System MUST show error messages for failed operations | P1 |
| FR-UI-005 | System MUST use Zustand for state management | P1 |
| FR-UI-006 | System MUST use Axios for HTTP requests | P1 |

---

## 4. Technical Architecture

### 4.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Next.js Frontend (Vercel)                    │  │
│  │  - React 19 Server & Client Components                   │  │
│  │  - Tailwind CSS + Shadcn/ui                             │  │
│  │  - Zustand State Management + Axios HTTP Client          │  │
│  │  - Better Auth Client                                    │  │
│  └──────────────────────┬───────────────────────────────────┘  │
└─────────────────────────┼──────────────────────────────────────┘
                          │ HTTPS + JWT
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Vercel)                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Authentication Middleware (JWT Validation)              │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │              API Routes                            │  │  │
│  │  │  GET    /api/{user_id}/tasks                      │  │  │
│  │  │  POST   /api/{user_id}/tasks                      │  │  │
│  │  │  GET    /api/{user_id}/tasks/{id}                 │  │  │
│  │  │  PUT    /api/{user_id}/tasks/{id}                 │  │  │
│  │  │  DELETE /api/{user_id}/tasks/{id}                 │  │  │
│  │  │  PATCH  /api/{user_id}/tasks/{id}/complete        │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │              Services Layer                        │  │  │
│  │  │  - TaskService                                    │  │  │
│  │  │  - AuthService                                    │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │              SQLModel ORM                          │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────┬───────────────────────────────────┘  │
└─────────────────────────┼──────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Neon Serverless PostgreSQL                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Tables:                                                  │  │
│  │  - users (managed by Better Auth)                        │  │
│  │  - tasks                                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | |
| Framework | Next.js 16+ (App Router) |
| Language | TypeScript 5.0+ |
| Styling | Tailwind CSS |
| Components | Shadcn/ui |
| State Management | Zustand |
| HTTP Client | Axios |
| Auth | Better Auth (JWT) |
| **Backend** | |
| Framework | FastAPI 0.115+ |
| Language | Python 3.13+ |
| ORM | SQLModel 0.0.24+ |
| Database | Neon PostgreSQL |
| Auth | JWT (via Better Auth) |
| Validation | Pydantic 2.0 |
| **Infrastructure** | |
| Frontend Hosting | Vercel |
| Backend Hosting | Vercel |
| Database | Neon Serverless |
| Package Manager | UV (Python) |

---

## 5. API Specification

### 5.1 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/{user_id}/tasks` | List all tasks for user |
| POST | `/api/{user_id}/tasks` | Create new task |
| GET | `/api/{user_id}/tasks/{id}` | Get task details |
| PUT | `/api/{user_id}/tasks/{id}` | Update task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion |

### 5.2 Request/Response Formats

#### Create Task Request
```json
POST /api/{user_id}/tasks
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

#### Create Task Response
```json
201 Created
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": "user_123",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2025-12-25T10:00:00Z",
    "updated_at": "2025-12-25T10:00:00Z"
  },
  "error": null
}
```

#### List Tasks Response
```json
200 OK
{
  "success": true,
  "data": [
    {
      "id": 1,
      "user_id": "user_123",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2025-12-25T10:00:00Z",
      "updated_at": "2025-12-25T10:00:00Z"
    }
  ],
  "error": null
}
```

#### Error Response
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token"
  }
}
```

---

## 6. Database Schema

### 6.1 Users Table
Managed by Better Auth.

| Column | Type | Constraints |
|--------|------|-------------|
| id | VARCHAR(255) | Primary Key |
| email | VARCHAR(255) | Unique, Not Null |
| name | VARCHAR(255) | Not Null |
| password_hash | VARCHAR(255) | Not Null |
| created_at | TIMESTAMP | Default now() |

### 6.2 Tasks Table

| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | Primary Key, Auto-increment |
| user_id | VARCHAR(255) | Foreign Key → users.id, Index |
| title | VARCHAR(200) | Not Null |
| description | TEXT | Max 1000 chars |
| completed | BOOLEAN | Default False |
| created_at | TIMESTAMP | Default now() |
| updated_at | TIMESTAMP | Default now() |

### 6.3 SQLModel Models

```python
# backend/models.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    tasks: list["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(back_populates="tasks")
```

---

## 7. State Management

### 7.1 Zustand Stores

#### Auth Store
```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthActions {
  login: (user: User, token: string) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
}
```

#### Task Store
```typescript
interface TaskState {
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
  filter: 'all' | 'active' | 'completed';
}

interface TaskActions {
  fetchTasks: () => Promise<void>;
  addTask: (title: string, description?: string) => Promise<void>;
  toggleTask: (id: number) => Promise<void>;
  deleteTask: (id: number) => Promise<void>;
  updateTask: (id: number, title: string, description?: string) => Promise<void>;
  setFilter: (filter: TaskState['filter']) => void;
}
```

### 7.2 Axios Configuration

```typescript
// frontend/lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  }
);

export { api };
```

---

## 8. Frontend Components

### 8.1 Component Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout with auth provider
│   ├── page.tsx            # Dashboard (protected)
│   ├── login/
│   │   └── page.tsx        # Login page
│   └── register/
│       └── page.tsx        # Register page
├── components/
│   ├── ui/                 # Shadcn/ui components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── checkbox.tsx
│   │   └── label.tsx
│   ├── auth/
│   │   ├── AuthProvider.tsx
│   │   └── ProtectedRoute.tsx
│   ├── task/
│   │   ├── TaskList.tsx
│   │   ├── TaskItem.tsx
│   │   ├── TaskForm.tsx
│   │   └── TaskCard.tsx
│   └── layout/
│       ├── Header.tsx
│       └── Sidebar.tsx
├── lib/
│   ├── api.ts              # Axios client
│   └── utils.ts
├── stores/
│   ├── useAuthStore.ts
│   └── useTaskStore.ts
└── types/
    └── index.ts
```

### 8.2 Key Components

#### TaskList Component
```typescript
// frontend/components/task/TaskList.tsx
'use client';

import { useTaskStore } from '@/stores/useTaskStore';
import { TaskItem } from './TaskItem';
import { Skeleton } from '@/components/ui/skeleton';

export function TaskList() {
  const { tasks, isLoading, filter } = useTaskStore();

  const filteredTasks = tasks.filter((task) => {
    if (filter === 'active') return !task.completed;
    if (filter === 'completed') return task.completed;
    return true;
  });

  if (isLoading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-20 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {filteredTasks.map((task) => (
        <TaskItem key={task.id} task={task} />
      ))}
      {filteredTasks.length === 0 && (
        <div className="text-center py-8 text-muted-foreground">
          No tasks yet. Add your first task!
        </div>
      )}
    </div>
  );
}
```

---

## 9. Backend Services

### 9.1 Project Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── models.py               # SQLModel database models
├── db.py                   # Database connection
├── auth.py                 # JWT verification middleware
├── routes/
│   ├── __init__.py
│   ├── auth.py             # Auth endpoints
│   └── tasks.py            # Task endpoints
├── schemas/
│   ├── __init__.py
│   ├── task.py             # Pydantic schemas
│   └── auth.py             # Auth schemas
└── services/
    ├── __init__.py
    └── task_service.py     # Business logic
```

### 9.2 Auth Middleware

```python
# backend/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Optional

security = HTTPBearer()
JWT_SECRET = "your-secret-key"  # From environment

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
```

### 9.3 Task Routes

```python
# backend/routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from db import get_session
from models import Task
from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from auth import get_current_user

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])

@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """List all tasks for the authenticated user."""
    result = await session.execute(
        select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    )
    tasks = result.scalars().all()
    return tasks

@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Create a new task for the authenticated user."""
    task = Task(user_id=user_id, **task_data.model_dump())
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
```

---

## 10. Better Auth Configuration

### 10.1 Frontend Setup

```typescript
// frontend/lib/auth.ts
import { createAuth } from 'better-auth';
import { jwtPlugin } from 'better-auth/plugins/jwt';

export const auth = createAuth({
  plugins: [
    jwtPlugin({
      jwtSecret: process.env.NEXT_PUBLIC_JWT_SECRET!,
    }),
  ],
  emailAndPassword: {
    enabled: true,
  },
});
```

### 10.2 Sign Up

```typescript
// frontend/app/register/page.tsx
'use client';

import { signUp } from '@/lib/auth';

export default function RegisterPage() {
  async function handleSubmit(formData: FormData) {
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;
    const name = formData.get('name') as string;

    const { data, error } = await signUp({
      email,
      password,
      name,
    });

    if (error) {
      // Show error
      return;
    }

    // Redirect to dashboard
    window.location.href = '/';
  }

  return (
    <form action={handleSubmit}>
      {/* Form fields */}
    </form>
  );
}
```

---

## 11. Implementation Phases

### Phase 2A: Foundation
1. Set up Next.js 16+ project with TypeScript and Tailwind CSS
2. Set up FastAPI project with UV and SQLModel
3. Configure Neon PostgreSQL database
4. Create database models (User, Task)

### Phase 2B: Authentication
1. Implement Better Auth on frontend
2. Create auth API endpoints on backend
3. Implement JWT verification middleware
4. Build login and register pages

### Phase 2C: Task CRUD
1. Implement task API endpoints
2. Create task components (TaskList, TaskItem, TaskForm)
3. Build task pages (dashboard)
4. Connect frontend to API with Axios

### Phase 2D: Polish
1. Add loading states and error handling
2. Implement optimistic UI updates
3. Add animations with Framer Motion
4. Ensure responsive design

---

## 12. Non-Functional Requirements

### 12.1 Performance
| Metric | Target |
|--------|--------|
| API Response Time | < 200ms |
| Page Load Time | < 2s |
| Time to Interactive | < 3s |
| Lighthouse Score | > 85 |

### 12.2 Security
| Requirement | Status |
|-------------|--------|
| JWT token validation | Required |
| User data isolation | Required |
| Password hashing (bcrypt) | Required |
| HTTPS in production | Required |
| Input validation | Required |
| Rate limiting (auth) | Required |

### 12.3 Availability
| Metric | Target |
|--------|--------|
| Uptime | 99.9% |
| Error Rate | < 0.1% |
| Data Loss | Zero |

---

## 13. Dependencies

### 13.1 Python Dependencies
```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
sqlmodel>=0.0.24
pydantic>=2.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
httpx>=0.28.0
python-multipart>=0.0.20
```

### 13.2 Node Dependencies
```
next@16.0.0
react@19.0.0
typescript@5.0.0
tailwindcss@4.0.0
better-auth@1.0.0
axios@1.7.0
zustand@5.0.0
framer-motion@11.0.0
```

---

## 14. Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_JWT_SECRET=your-jwt-secret
```

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=your-better-auth-secret
JWT_SECRET=your-jwt-secret
CORS_ORIGINS=http://localhost:3000
```

---

## 15. Success Criteria

### Functional
- [ ] All user stories are implemented
- [ ] All API endpoints are working
- [ ] User can register, login, logout
- [ ] User can create, view, edit, delete tasks
- [ ] User can toggle task completion
- [ ] User data is isolated by user_id

### Technical
- [ ] Next.js 16+ with App Router
- [ ] FastAPI backend with SQLModel
- [ ] Zustand for state management
- [ ] Axios for HTTP requests
- [ ] JWT authentication working
- [ ] Neon PostgreSQL connected

### Performance
- [ ] Lighthouse score > 85
- [ ] API response time < 200ms
- [ ] Responsive design works on mobile

---

**Specification Version**: 2.0.0
**Created**: 2025-12-25
**Status**: Ready for Planning

---

## Next Steps

Run the following Spec-Kit Plus commands to proceed:

1. **Generate Plan**: `@sp.plan` - Create implementation plan from this specification
2. **Generate Tasks**: `@sp.tasks` - Break plan into actionable tasks
3. **Implement**: `@sp.implement` - Execute tasks sequentially

**Reference**: Always refer to `constitution-prompt-phase-2.md` for project principles and constraints.

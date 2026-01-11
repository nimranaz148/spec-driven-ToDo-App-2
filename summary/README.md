# WhisperDo - Just Whisper It, Done.

A modern, AI-powered todo application built using **Spec-Driven Development** with Claude Code and Spec-Kit Plus.

> **WhisperDo** - AI-powered task management through natural conversation. Just whisper your tasks and watch them happen.

## Current Phase: Phase 3 - AI-Powered Todo Chatbot

Transform the Phase 2 web application into an AI-powered chatbot interface with natural language task management.

### Phase 3 Features

- **AI Chatbot Interface** - Natural language task management through conversation with **dual UI options**
- **OpenAI Agents SDK** - Gemini 2.5 Flash-powered AI assistant
- **MCP Server** - FastMCP with 5 task operation tools (add, list, complete, delete, update)
- **SSE Streaming** - Real-time response streaming with token-by-token display
- **Conversation History** - Persistent chat storage with sidebar navigation and conversation switching
- **Dual Chat UI Options**:
  - **ChatKit UI** - Production-ready chat interface from OpenAI with theming support
  - **Custom UI** - Enhanced custom chat interface with advanced streaming visualization
- **UI Toggle** - Switch between ChatKit and Custom UI seamlessly during conversations
- **Analytics Dashboard** - Interactive charts with Recharts (Productivity Trend, Task Distribution, Status Overview)
- **Loading Indicators** - Visual feedback during AI processing
- **Auto-scroll** - Automatic scrolling to new messages
- **Keyboard Shortcuts** - Enter to send, Shift+Enter for newline
- **Error Handling** - Graceful error messages with rate limit detection and user-friendly notifications
- **Security** - Rate limiting, input sanitization, and prompt injection protection

### Chat Interface Options

Users can choose between two chat interfaces, each with unique advantages:

#### **ChatKit UI** (Default)
- Professional OpenAI ChatKit interface
- Clean, minimalist design
- Standard chat experience
- Built-in theming support
- Quick message sending

#### **Custom UI**
- Enhanced streaming visualization
- Real-time thinking steps display
- Tool call progress indicators
- Rich markdown rendering with syntax highlighting
- Conversation history with timestamps
- Processing time metrics
- Advanced error handling with actionable feedback
- Better context for rate limit errors

**Switch Between UIs**: Use the toggle button at the top of the chat page to switch between ChatKit and Custom interfaces at any time.

### Hybrid Voice + AI Chat Interface

The Voice Assistant page now features a **Hybrid UI** that combines voice commands with real AI chat:

- **Real AI Integration** - Voice commands are processed by the Gemini-powered AI agent (not dummy responses)
- **Multi-stage Speech Feedback** - Hear "Thinking...", tool notifications, and final responses
- **Streaming Responses** - Real-time token streaming with visual indicators
- **Task List Cards** - Beautiful card-based UI for task lists with priority badges
- **Conversation History Panel** - Toggle sidebar to view chat history
- **New Chat Button** - Start fresh conversations while preserving history
- **Verbose Mode Toggle** - Switch between verbose/compact streaming indicators
- **Example Commands** - Clickable command suggestions for quick testing
- **Context Awareness** - Follow-up questions maintain conversation context

### Natural Language Commands

Talk to the AI assistant naturally to manage your tasks:

| Intent | Example Commands |
|--------|------------------|
| **Add Task** | "Add a task to buy groceries", "I need to remember to call mom", "Create task: finish report" |
| **List Tasks** | "Show me all my tasks", "What's pending?", "What have I completed?" |
| **Complete Task** | "Mark task 3 as complete", "I finished buying groceries", "Complete the meeting task" |
| **Delete Task** | "Delete task 2", "Remove the old meeting task" |
| **Update Task** | "Change task 1 to 'Call mom tonight'", "Update task 2 description to 'Include milk and eggs'" |

### Phase 3 Tech Stack

**AI/Agent Layer:**
- OpenAI Agents SDK (Agent orchestration)
- LiteLLM (Gemini 2.5 Flash integration)
- FastMCP (MCP server framework)

**Backend Additions:**
- sse-starlette (Server-Sent Events)
- httpx (Async HTTP client)

**Frontend Additions:**
- OpenAI ChatKit (Chat UI components)
- eventsource-parser (SSE parsing)

---

## Phase 2: Full-Stack Web Application (COMPLETE)

A production-ready web application with persistent storage, Better Auth authentication, and multi-user support.

### Features Implemented

- **User Authentication** - Better Auth with JWT tokens (signup, login, logout)
- **Task Management** - Full CRUD operations (Create, Read, Update, Delete)
- **Optimistic Updates** - Immediate UI feedback for all operations
- **Smooth Animations** - Framer Motion transitions for state changes
- **Real-time Validation** - React Hook Form + Zod schemas
- **Error Handling** - Toast notifications for success/error states
- **Responsive Design** - Mobile-first Tailwind CSS styling
- **User Isolation** - Tasks are private to each user
- **Voice Assistant** - Voice commands to create and complete tasks
- **Task Filtering** - Filter by status, priority
- **Task Sorting** - Sort by date, priority, title
- **Analytics Dashboard** - Task statistics and insights

### Tech Stack

**Frontend:**
- Next.js 16+ (App Router, React 19)
- TypeScript
- Tailwind CSS 4.0
- Zustand (State Management)
- Axios (HTTP Client)
- Shadcn/ui + Aceternity UI Components
- Framer Motion Animations
- Better Auth (Client-side authentication)

**Backend:**
- Python 3.13+ with UV
- FastAPI 0.115+
- SQLModel 0.0.24+ ORM
- PostgreSQL (Neon Serverless)
- Better Auth JWT Validation (JWKS)

---

## Architecture

### System Overview

```
+--------------------+       +----------------------+       +------------------+
|                    |       |                      |       |                  |
|   Next.js Frontend |<----->|   FastAPI Backend    |<----->|   Neon PostgreSQL|
|   (Vercel)         |       |   (Port 8000)        |       |                  |
|                    |       |                      |       +------------------+
|   - ChatKit UI     |       |   - JWT Auth         |
|   - Zustand Store  |       |   - Chat Router      |       +------------------+
|   - SSE Client     |       |   - OpenAI Agents    |<----->|   FastMCP Server |
|                    |       |     SDK              |       |   (Port 8001)    |
+--------------------+       +----------------------+       |                  |
                                      |                     |   - add_task     |
                                      v                     |   - list_tasks   |
                              +---------------+             |   - complete_task|
                              |  Gemini 2.5   |             |   - delete_task  |
                              |  Flash API    |             |   - update_task  |
                              +---------------+             +------------------+
```

### MCP Tools

> **Note:** User identity is automatically injected from the authenticated session. Tools don't require `user_id` parameter - task isolation is enforced server-side.

| Tool | Parameters | Returns | Description |
|------|------------|---------|-------------|
| `add_task` | title, description?, priority?, due_date?, is_recurring?, recurrence_pattern? | {task_id, status, title, priority, due_date} | Create new task |
| `list_tasks` | status?, priority? | {total, pending_count, completed_count, tasks: [...]} | List user's tasks with filters |
| `complete_task` | task_id | {task_id, status, title} | Mark task complete |
| `delete_task` | task_id | {task_id, status, title} | Delete task |
| `update_task` | task_id, title?, description?, priority?, due_date?, completed?, is_recurring?, recurrence_pattern? | {task_id, status, title, ...} | Update task details |

---

## Project Structure

```
WhisperDo/
├── frontend/                 # Next.js application
│   ├── app/                  # Next.js App Router pages
│   │   ├── (auth)/          # Auth pages (login, signup)
│   │   ├── (dashboard)/     # Dashboard pages
│   │   └── chat/            # Chat page (Phase 3)
│   ├── components/          # React components
│   │   ├── ui/              # Shadcn/ui components
│   │   ├── tasks/           # Task components
│   │   ├── chat/            # Chat components (Phase 3)
│   │   └── conversation/    # Conversation sidebar (Phase 3)
│   ├── stores/              # Zustand stores
│   │   ├── auth-store.ts
│   │   ├── task-store.ts
│   │   └── conversation-store.ts (Phase 3)
│   └── lib/                 # Utilities and API client
│       ├── api/             # Axios API modules
│       └── sse/             # SSE client (Phase 3)
│
├── backend/                  # FastAPI application
│   ├── src/
│   │   ├── models/          # SQLModel database models
│   │   ├── services/        # Business logic
│   │   ├── routers/         # API routes
│   │   ├── agents/          # AI Agent code (Phase 3)
│   │   ├── mcp_server/      # FastMCP server (Phase 3)
│   │   └── schemas/         # Pydantic schemas
│   ├── tests/               # Pytest tests
│   └── alembic/             # Database migrations
│
├── specs/                    # Feature specifications
│   ├── 001-phase-2-web-app/ # Phase 2 specs
│   ├── features/            # Feature specs
│   ├── api/                 # API documentation
│   ├── database/            # Schema specifications
│   └── ui/                  # Component & page specs
│
├── .claude/                  # Claude Code configuration
│   ├── agents/              # Specialized development agents (with skills coupling)
│   │   ├── backend-api-builder.md   # skills: chatkit-backend, better-auth-integration
│   │   ├── frontend-ui-builder.md
│   │   ├── database-designer.md
│   │   ├── ai-agent-builder.md      (Phase 3)
│   │   ├── mcp-server-builder.md    (Phase 3)
│   │   └── chatbot-ui-builder.md    # skills: chatkit-frontend, conversation-management
│   └── skills/              # Setup & configuration skills
│       ├── fastapi-setup/
│       ├── nextjs-setup/
│       ├── shadcn-ui-setup/
│       ├── neon-db-setup/
│       ├── better-auth-integration/
│       ├── openai-agents-setup/       (Phase 3)
│       ├── fastmcp-server-setup/      (Phase 3)
│       ├── chatkit-frontend/          (Phase 3) - ChatKit React + useChatKit
│       ├── chatkit-backend/           (Phase 3) - SSE endpoint + conversations
│       └── conversation-management/   (Phase 3)
│
├── history/                  # PHRs and ADRs
│   ├── prompts/             # Prompt History Records
│   └── adr/                 # Architecture Decision Records
│
├── prompts/                  # Phase 2 core prompts (reference)
│   ├── constitution-prompt-phase-2.md
│   ├── spec-prompt-phase-2.md
│   └── plan-prompt-phase-2.md
│
├── constitution-prompt-phase-3.md    # Phase 3 constitution
├── spec-prompt-phase-3.md            # Phase 3 specification
├── plan-prompt-phase-3.md            # Phase 3 implementation plan
└── CLAUDE.md                         # Root agent orchestrator
```

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 20+
- PostgreSQL or Neon account
- UV package manager (`pip install uv`)
- Gemini API Key (for Phase 3 AI features)

### Backend Setup

```bash
cd backend
uv sync                    # Install dependencies
cp .env.example .env       # Configure environment
# Edit .env with your database URL and API keys
uv run alembic upgrade head       # Run migrations
uv run uvicorn src.main:app --reload
```

Backend will run at http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install                # Install dependencies
cp .env.example .env.local # Configure environment
# Edit .env.local with API URL
npm run dev                # Start dev server
```

Frontend will run at http://localhost:3000

### Phase 3 AI Chatbot Setup

```bash
# 1. Install backend AI dependencies
cd backend
uv add openai-agents fastmcp litellm sse-starlette httpx

# 2. Install frontend chat dependencies
cd frontend
npm install eventsource-parser

# 3. Configure Gemini API key in backend/.env
GEMINI_API_KEY=your-gemini-api-key-here
```

### Running All Three Servers (Phase 3)

Phase 3 requires **three servers** running simultaneously. Open three terminal windows:

**Terminal 1 - MCP Server (Port 8001):**
```bash
cd backend
uv run python -m src.mcp_server.server
# Output: 🚀 Starting Todo MCP Server on http://0.0.0.0:8001
```

**Terminal 2 - FastAPI Backend (Port 8000):**
```bash
cd backend
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
# Output: Uvicorn running on http://0.0.0.0:8000
```

**Terminal 3 - Next.js Frontend (Port 3000):**
```bash
cd frontend
npm run dev
# Output: Ready on http://localhost:3000
```

### Quick Start Commands (Copy-Paste Ready)

```bash
# Option 1: Run all in background (Linux/Mac)
cd backend && uv run python -m src.mcp_server.server &
cd backend && uv run uvicorn src.main:app --reload &
cd frontend && npm run dev &

# Option 2: Using separate terminals
# Terminal 1:
cd backend && uv run python -m src.mcp_server.server

# Terminal 2:
cd backend && uv run uvicorn src.main:app --reload

# Terminal 3:
cd frontend && npm run dev
```

### Server URLs

| Server | URL | Purpose |
|--------|-----|---------|
| MCP Server | http://localhost:8001 | FastMCP task tools (AI agent connects here) |
| Backend API | http://localhost:8000 | FastAPI REST endpoints + Chat API |
| Frontend | http://localhost:3000 | Next.js web application |
| API Docs | http://localhost:8000/docs | Swagger UI documentation |

### Accessing the Chat Interface

1. Navigate to http://localhost:3000
2. Log in with your account
3. Click "Chat" in the navigation
4. Start typing natural language commands to manage tasks

---

## Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host/db

# Auth
BETTER_AUTH_SECRET=your-secret-key
BETTER_AUTH_URL=http://localhost:3000

# CORS
CORS_ORIGINS=http://localhost:3000

# Phase 3 - AI Configuration
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash

# Phase 3 - MCP Server
MCP_SERVER_URL=http://localhost:8001
MCP_SERVER_PORT=8001
```

### Frontend (.env.local)

```env
# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# ChatKit (for production deployment)
# Get domain key from: https://platform.openai.com/settings/organization/security/domain-allowlist
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here
```

### Getting API Keys

**Gemini API Key:**
1. Visit https://ai.google.dev/
2. Sign in with Google account
3. Navigate to "Get API Key"
4. Create a new API key
5. Copy to `GEMINI_API_KEY` in backend/.env

**ChatKit Domain Allowlist (Production Only):**
1. Deploy frontend to get URL (e.g., `https://your-app.vercel.app`)
2. Add domain at: https://platform.openai.com/settings/organization/security/domain-allowlist
3. Copy domain key to `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`
4. Note: localhost works without configuration

---

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Phase 2 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{user_id}/tasks` | List all tasks |
| POST | `/api/{user_id}/tasks` | Create task |
| GET | `/api/{user_id}/tasks/{id}` | Get task |
| PUT | `/api/{user_id}/tasks/{id}` | Update task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle complete |

### Phase 3 Chat Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/{user_id}/chat` | Send message (non-streaming) |
| POST | `/api/{user_id}/chat/stream` | Send message (SSE streaming) |
| GET | `/api/{user_id}/conversations` | List conversations |
| GET | `/api/{user_id}/conversations/{id}` | Get conversation with messages |
| DELETE | `/api/{user_id}/conversations/{id}` | Delete conversation |

### Chat Request/Response Format

**Request:**
```json
{
  "conversation_id": 123,  // optional - creates new if not provided
  "message": "Add a task to buy groceries"
}
```

**Response (non-streaming):**
```json
{
  "success": true,
  "data": {
    "conversation_id": 123,
    "message_id": 456,
    "response": "I've added 'Buy groceries' to your task list.",
    "tool_calls": [
      {
        "tool": "add_task",
        "args": {"title": "Buy groceries"},
        "result": {"task_id": 789, "status": "created"}
      }
    ]
  }
}
```

**Response (SSE streaming):**
```
event: token
data: {"content": "I've "}

event: token
data: {"content": "added "}

event: tool_call
data: {"tool": "add_task", "args": {"title": "Buy groceries"}}

event: tool_result
data: {"task_id": 789, "status": "created"}

event: done
data: {"conversation_id": 123, "message_id": 456}
```

---

## Performance & Security

### Performance Targets

| Metric | Target |
|--------|--------|
| First token latency | < 2 seconds |
| Full response time | < 30 seconds |
| MCP tool execution | < 500ms |
| Conversation load | < 1 second |
| Concurrent sessions | 100+ |

### Security Measures

- **JWT Authentication**: All chat endpoints require valid JWT tokens
- **User Isolation**: Users can only access their own conversations and tasks
- **Rate Limiting**: 30 messages/minute per user (enforced by middleware)
- **Input Validation**: Message length limited to 4000 characters (enforced by Pydantic)
- **Input Sanitization**: Protection against prompt injection attacks (automatic sanitization)
- **Graceful Error Handling**: User-friendly error messages for AI model failures
- **Audit Trail**: Tool calls are logged for security review
- **HTTPS Required**: All production traffic uses HTTPS encryption

---

## Skills & Agents

This project uses Claude Code with specialized agents coupled to skills for efficient development.

### Active Skills (Phase 3)

| Skill | Purpose | Agent Coupled |
|-------|---------|---------------|
| `chatkit-frontend` | ChatKit React UI, useChatKit hook, theming | `chatbot-ui-builder` |
| `chatkit-backend` | SSE endpoint, conversation persistence | `backend-api-builder` |
| `conversation-management` | Conversation sidebar, history UI | `chatbot-ui-builder` |
| `openai-agents-setup` | OpenAI Agents SDK + Gemini | `ai-agent-builder` |
| `fastmcp-server-setup` | FastMCP server with task tools | `mcp-server-builder` |

### Deprecated Skills

| Old Skill | Use Instead |
|-----------|-------------|
| `openai-chatkit-setup` | `chatkit-frontend` |
| `streaming-sse-setup` | `chatkit-backend` |
| `chat-api-integration` | `chatkit-backend` |

### Skill Files Structure

Each skill follows this structure:
```
.claude/skills/<skill-name>/
├── SKILL.md          # Main skill file (required)
├── examples.md       # Code examples (optional)
├── REFERENCE.md      # API reference (optional)
└── templates/        # Code templates (optional)
```

### Agent-Skill Coupling

Agents declare coupled skills in frontmatter:
```yaml
---
name: chatbot-ui-builder
skills: chatkit-frontend, conversation-management
---
```

---

## Development Methodology

This project follows **Spec-Driven Development**:

1. **Constitution** - Define project principles and constraints
2. **Specification** - Write user stories and acceptance criteria
3. **Plan** - Create implementation architecture
4. **Tasks** - Break down into testable tasks
5. **Implement** - Generate code with Claude Code
6. **Document** - Record decisions in PHRs and ADRs

### Available Slash Commands

```bash
/sp.constitution  # Define project principles
/sp.specify       # Create feature specification
/sp.plan          # Generate implementation plan
/sp.tasks         # Break plan into tasks
/sp.implement     # Execute implementation
/sp.clarify       # Ask clarifying questions
/sp.analyze       # Analyze existing code
/sp.checklist     # Generate completion checklist
/sp.adr           # Document architecture decision
/sp.phr           # Create prompt history record
/sp.git.commit_pr # Commit and create PR
```

---

## See Also

- [CLAUDE.md](./CLAUDE.md) - Root agent orchestrator
- [Phase 3 Constitution](./constitution-prompt-phase-3.md)
- [Phase 3 Specification](./spec-prompt-phase-3.md)
- [Phase 3 Plan](./plan-prompt-phase-3.md)
- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)

### External Documentation

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [OpenAI ChatKit](https://platform.openai.com/docs/guides/chatkit)
- [Gemini API](https://ai.google.dev/docs)

---

## License

MIT
CORS_ORIGIN=http://localhost:3000
LOG_LEVEL=INFO
EOF

# Update the .env file with your actual database credentials

# Run database migrations
python -c "from src.db import create_tables; import asyncio; asyncio.run(create_tables())"

# Start the backend server
uvicorn src.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from root)
cd frontend

# Install dependencies
npm install

# Create .env.local file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-strong-secret-key-change-this-in-production
EOF

# Make sure BETTER_AUTH_SECRET matches the backend value

# Start the development server
npm run dev
```

Frontend will be available at: http://localhost:3000

### 4. Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

## Development

### Backend Development

```bash
cd backend

# Run with auto-reload
uvicorn src.main:app --reload --port 8000

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Frontend Development

```bash
cd frontend

# Development server
npm run dev

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Using Docker Compose

Run both frontend and backend together:

```bash
# Start all services
docker-compose up

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Environment Variables

### Backend (.env)

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `BETTER_AUTH_SECRET` | JWT secret key (min 32 chars) | Yes | - |
| `CORS_ORIGIN` | Allowed CORS origins | No | `http://localhost:3000` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No | `INFO` |

**Important**: Never commit `.env` files to version control. Use `.env.example` as a template.

### Frontend (.env.local)

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | Yes | - |
| `BETTER_AUTH_SECRET` | JWT secret (must match backend) | Yes | - |

## Features

### Implemented User Stories

- [x] **User Registration & Login (US1)**: Secure account creation and authentication
- [x] **Task CRUD Operations (US2)**: Create, read, update, and delete tasks
- [x] **User Logout (US3)**: Secure session termination
- [x] **Toggle Task Completion (US4)**: Mark tasks as complete/incomplete
- [x] **User Data Isolation (US5)**: Users can only access their own tasks
- [x] **Responsive UI & Polish (US6)**: Mobile-first design with animations

### Security Features

- JWT-based authentication with token blacklisting
- Bcrypt password hashing with automatic salt generation
- Rate limiting (60 requests/minute per user)
- CORS protection
- SQL injection prevention via parameterized queries
- XSS prevention via React's built-in escaping
- Input validation with Pydantic and Zod
- Secure headers and HTTPS enforcement (production)

### API Features

- RESTful API design
- Comprehensive OpenAPI/Swagger documentation
- Request/response validation
- Structured error responses
- Rate limit headers
- Request ID tracking
- Response time metrics

## Testing

### Backend Tests

Located in `backend/tests/`:
- Unit tests for models, services, and utilities
- Integration tests for API endpoints
- Contract tests for API specifications
- Test coverage: 80%+

```bash
cd backend
pytest
pytest --cov=src --cov-report=html
```

### Frontend Tests

Located in `frontend/tests/`:
- Component tests with React Testing Library
- Integration tests for user flows
- Form validation tests
- Test coverage: 70%+

```bash
cd frontend
npm test
npm run test:coverage
```

## API Documentation

Complete API documentation is available at:
- Interactive docs: http://localhost:8000/docs (Swagger UI)
- Reference docs: http://localhost:8000/redoc (ReDoc)
- Markdown docs: [docs/api.md](docs/api.md)

### Key Endpoints

**Authentication**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user

**Tasks**
- `GET /api/{user_id}/tasks` - List all tasks
- `POST /api/{user_id}/tasks` - Create task
- `GET /api/{user_id}/tasks/{id}` - Get task details
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion

## Monitoring & Observability

### Logging

The backend implements structured JSON logging with:
- Request ID tracking for distributed tracing
- Response time metrics
- Authentication event logging
- Database error logging
- No sensitive data in logs (passwords, tokens)

### Health Checks

- `GET /health` - Application health status
- Database connection verification
- JWT secret validation

## Deployment

See [docs/deployment.md](docs/deployment.md) for comprehensive deployment instructions including:
- Production environment setup
- Database migrations
- Frontend build and deployment
- Backend deployment strategies
- Environment variable configuration
- Health checks and monitoring
- CI/CD integration

## Contributing

This project follows spec-driven development using GitHub Spec-Kit:

1. Review specifications in `/specs`
2. Reference specs when implementing: `@specs/features/file.md`
3. Update specs if requirements change
4. Follow the implementation workflow:
   - Read spec → Implement backend → Implement frontend → Test

## Documentation

- [Project Overview](specs/overview.md)
- [API Reference](docs/api.md)
- [Security Review](docs/security.md)
- [Deployment Guide](docs/deployment.md)
- [Quickstart Guide](specs/1-todo-web-app/quickstart.md)
- [Feature Specifications](specs/features/)
- [Database Schema](specs/database/schema.md)

## Troubleshooting

### Common Issues

**CORS Errors**
```bash
# Check that CORS_ORIGIN in backend .env matches your frontend URL
CORS_ORIGIN=http://localhost:3000
```

**Database Connection Failed**
```bash
# Verify DATABASE_URL format
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
# Ensure Neon database is active and credentials are correct
```

**JWT Errors**
```bash
# Ensure BETTER_AUTH_SECRET matches between frontend and backend
# Must be at least 32 characters for production
```

**Rate Limit Issues**
```bash
# Check headers in response:
# X-RateLimit-Limit: 60
# X-RateLimit-Remaining: 59
# X-RateLimit-Reset: 1735315200
```

**Port Already in Use**
```bash
# Backend (8000)
lsof -ti:8000 | xargs kill -9

# Frontend (3000)
lsof -ti:3000 | xargs kill -9
```

## Performance

- Backend API response time: < 200ms (p95)
- Frontend Lighthouse score: > 85
- Database query optimization with indexes
- Optimistic UI updates for better UX
- Lazy loading and code splitting

## Browser Support

- Chrome/Edge: Last 2 versions
- Firefox: Last 2 versions
- Safari: Last 2 versions
- Mobile: iOS 14+, Android 10+

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions:
1. Check existing documentation in `/docs` and `/specs`
2. Review [Troubleshooting](#troubleshooting) section
3. Open an issue with detailed description and logs

## Acknowledgments

Built with:
- [Next.js](https://nextjs.org/) - React framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [SQLModel](https://sqlmodel.tiangolo.com/) - SQL database ORM
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS
- [Better Auth](https://www.better-auth.com/) - Authentication library
- [Shadcn/ui](https://ui.shadcn.com/) - UI component library
- [Neon](https://neon.tech/) - Serverless PostgreSQL

---

**Version**: 1.0.0
**Last Updated**: 2025-12-27
**Generated with**: Spec-Kit Plus

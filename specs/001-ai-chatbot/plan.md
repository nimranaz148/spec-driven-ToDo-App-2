# Implementation Plan: AI-Powered Todo Chatbot - Phase 3

**Branch**: `001-ai-chatbot` | **Date**: 2026-01-03 | **Spec**: [specs/001-ai-chatbot/spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ai-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Phase 3 delivers a conversational interface that lets authenticated users create, inspect, update, complete, and delete todos with natural language while persisting the full chat history for later review (`specs/001-ai-chatbot/spec.md:10-104`). The implementation adds an Official MCP server exposing task tools, wires it to a Gemini 2.5 Flash model via AsyncOpenAI/FastMCP, adds a FastAPI chat endpoint that enforces JWT user isolation, and extends the Next.js dashboard chat page (ChatKit-first, Tailwind fallback) to call the new API with optimistic UI updates.

## Final Architecture & Implementation Status

### ✅ Completed Components

**Backend Infrastructure**:
- ✅ MCP Server with full CRUD tools (create_task, list_tasks, update_task, complete_task, delete_task)
- ✅ OpenAI Agents SDK integration with Gemini 2.5 Flash model
- ✅ FastMCP HTTP transport for tool communication
- ✅ Conversation & Message SQLModel entities with proper relationships
- ✅ JWT-based user isolation and authentication
- ✅ Rate limiting middleware (30 req/min per user)
- ✅ Structured logging with request tracing

**Chat API Endpoints**:
- ✅ `POST /api/{user_id}/chat` - Standard chat with tool calls
- ✅ `POST /api/{user_id}/chat/stream` - Server-sent events streaming
- ✅ `GET /api/{user_id}/chat/history` - Full conversation history
- ✅ Bulk operation confirmation workflow with tokens
- ✅ Tool call metadata and thinking steps in responses

**Frontend Components**:
- ✅ ChatKit-based UI with optimistic updates
- ✅ Streaming response support with real-time typing
- ✅ Confirmation modal for destructive operations
- ✅ Error handling with retry guidance
- ✅ Chat history persistence across page reloads
- ✅ Zustand store with server state reconciliation

### 🔄 Confirmation Flow Architecture

**Bulk Operation Detection**:
1. Agent runner detects patterns like "delete all tasks" or "complete everything"
2. Generates secure confirmation token and stores pending action
3. Returns `confirmation_required` response instead of executing

**User Confirmation Process**:
1. Frontend displays confirmation modal with affected items
2. User clicks "Confirm" → sends original message with `confirm_token`
3. Backend validates token, executes bulk operation, clears token
4. User clicks "Cancel" → frontend shows cancellation message

**Security Features**:
- Tokens expire after 5 minutes
- User ID validation prevents token hijacking
- Clear audit trail of confirmed vs cancelled actions

### 📊 Context Management

**Sliding Window Implementation**:
- Full conversation history persisted in database
- Agent receives last 20 messages for context
- References like "that task" resolved using conversation history
- Optimized queries with proper indexing

**Reference Resolution**:
- "that task" → most recently mentioned task
- "the first one" → first task in last list shown  
- "my meeting task" → fuzzy match on task titles
- Ambiguous references trigger clarification prompts

**Language/Version**: Python 3.13 (backend), TypeScript 5 + React 19 + Next.js 15 (frontend)
**Primary Dependencies**: FastAPI, SQLModel, AsyncOpenAI SDK (Gemini 2.5 Flash), FastMCP + Official MCP SDK, LiteLLM (fallback transport), JWT auth via Better Auth, Next.js App Router, Tailwind CSS, Zustand
**Storage**: Neon/PostgreSQL via SQLModel models for tasks, conversations, and messages
**Testing**: pytest + pytest-asyncio for backend (unit/service/integration), Jest + Testing Library for components, Playwright for end-to-end chat flows
**Target Platform**: Linux containerized FastAPI service + Vercel-hosted Next.js frontend (desktop + mobile web)
**Project Type**: Web application (monorepo with `backend/` and `frontend/`)
**Performance Goals**: Meet SC-001—chat round trip (send → AI response) under 5 seconds for CRUD operations; maintain smooth scrolling at 60fps on chat page
**Constraints**: Strict user isolation (SC-004), persistent message logging (SC-003), confirmation for destructive bulk commands, max 4000-char inputs, optional rate limiting (30 req/min/user)
**Scale/Scope**: Single conversation per user for Phase 3, sliding context window of ~20 recent messages per LLM call (`specs/001-ai-chatbot/spec.md:41-76`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Description | Status | Notes |
|------|-------------|--------|-------|
| G1 | Spec-driven workflow: plan, research, data-model, quickstart, and contracts must exist before coding | ✅ | This plan enumerates required artifacts and blocks implementation until they exist. |
| G2 | Test-first mandate: new functionality requires unit + integration coverage (backend + frontend) before merge | ✅ | Testing strategy covers MCP tools, agent wrappers, chat API, and chat UI interactions. |
| G3 | Security & isolation: JWT user_id parity, scoped DB queries, and confirmation for bulk actions | ✅ | Chat endpoint design enforces `user_id == current_user.id`, MCP tools filter by user, UI prompts for destructive commands. |

(Re-check after Phase 1: ensure generated contracts + data model still respect gates; update if new risks appear.)

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-chatbot/
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 findings
├── data-model.md        # Phase 1 entity + schema design
├── quickstart.md        # Phase 1 developer guide
├── contracts/           # OpenAPI contracts for chat endpoints
└── tasks.md             # Phase 2 execution tasks (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── pyproject.toml
├── src/
│   ├── main.py              # FastAPI app + router registration
│   ├── models.py            # SQLModel Task (extend with Conversation/Message)
│   ├── db.py                # Session + engine helpers
│   ├── auth.py              # JWT verification (Better Auth tokens)
│   ├── routes/
│   │   ├── tasks.py         # Existing CRUD endpoints
│   │   └── chat.py          # NEW: chat endpoint + rate limiting
│   ├── services/
│   │   ├── task_service.py  # Existing task logic
│   │   └── conversation_service.py  # NEW: conversation/message helpers
│   ├── agent/               # NEW: agent config, tools, runner
│   └── mcp_server.py        # NEW: Official MCP server exposing task tools
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/

frontend/
├── package.json
├── src/
│   ├── app/
│   │   ├── dashboard/
│   │   │   ├── chat/page.tsx    # Enhanced ChatKit/Tailwind UI
│   │   │   └── tasks/page.tsx
│   │   └── layout.tsx
│   ├── components/
│   │   ├── chat/
│   │   │   ├── chat-feed.tsx    # NEW reusable chat feed
│   │   │   └── confirmation.tsx # NEW destructive-action dialog
│   │   └── ui/*
│   ├── lib/api.ts              # Add sendChatMessage()
│   └── stores/task-store.ts
└── tests/
    ├── components/
    └── e2e/
```

**Structure Decision**: Continue using the existing monorepo split between `backend/` (FastAPI) and `frontend/` (Next.js). All Phase 3 backend additions live under `backend/src/{routes,services,agent}`, and frontend chat work lives under `frontend/src/app/dashboard/chat` plus shared `components/chat`. No extra packages or services are introduced.

## Complexity Tracking

_No constitution violations identified; no additional complexity justification required._

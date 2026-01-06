# Tasks: AI-Powered Todo Chatbot - Phase 3

**Input**: `specs/001-ai-chatbot/{plan.md,spec.md,research.md,data-model.md,contracts/chat-openapi.yaml,quickstart.md}`
**Prerequisites**: Constitution gates G1-G3 satisfied (plan.md:24-35)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Ensure environment configs and developer docs exist before implementation.

- [X] T001 Create `backend/.env.example` with `DATABASE_URL`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `JWT_SECRET`, `RATE_LIMIT_PER_MINUTE` placeholders (backend/.env.example)
- [X] T002 Create `frontend/.env.local.example` exposing `NEXT_PUBLIC_API_BASE_URL` and Better Auth config (frontend/.env.local.example)
- [X] T003 [P] Update `specs/001-ai-chatbot/quickstart.md` with MCP server run instructions and chat endpoint testing steps (specs/001-ai-chatbot/quickstart.md)
- [X] T004 [P] Add `make chat-dev` (or npm script) wiring backend + MCP server startup docs in `CLAUDE.md` tooling section (CLAUDE.md)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database, services, and agent scaffolding that every story depends on.

- [X] T005 Extend SQLModel definitions with `Conversation` and `Message` entities per data-model (backend/src/models.py)
- [X] T006 Generate Alembic migration creating `conversations` + `messages` tables with indexes + FK cascade (backend/migrations/versions/*_conversation_message.py)
- [X] T007 [P] Create `backend/src/services/conversation_service.py` with helpers: `get_or_create_conversation(user_id)`, `append_message(...)`, `list_recent_messages(...)`
- [X] T008 [P] Add unit tests for conversation/message models & service behaviors (backend/tests/unit/test_conversation_service.py)
- [X] T009 Scaffold Official MCP server exposing task CRUD tool placeholders (backend/src/mcp_server.py)
- [X] T010 Configure FastMCP + AsyncOpenAI client + Gemini model settings (backend/src/agent/config.py)
- [X] T011 Implement shared JWT guard + dependency injection utilities reused by chat routes (backend/src/auth.py)
- [X] T012 [P] Document new DB entities and MCP components in `specs/001-ai-chatbot/data-model.md` & `plan.md` references (specs/001-ai-chatbot/data-model.md)

**Checkpoint**: Database + agent plumbing ready; user stories can begin.

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can create todos by sending natural language to the chatbot.
**Independent Test**: Send "Add a task to buy groceries" via `/api/{user_id}/chat`; verify assistant confirmation and task persisted (spec.md:16-22).

### Tests (required by constitution)
- [X] T013 [P] [US1] Add contract test covering `POST /api/{user_id}/chat` happy path + validation errors (backend/tests/contract/test_chat_create_task.py)
- [X] T014 [P] [US1] Add integration test simulating user message → task creation via MCP tool (backend/tests/integration/test_chat_create_task.py)
- [X] T015 [P] [US1] Add frontend component test ensuring send action triggers optimistic message bubble (frontend/tests/components/chat/chat-feed.test.tsx)

### Implementation
- [X] T016 [P] [US1] Implement MCP task tool `create_task(title, description?)` calling TaskService (backend/src/mcp_server.py - all CRUD tools implemented)
- [X] T017 [US1] Implement Gemini prompt + FastMCP runner translating natural language create intents (backend/src/agent/runner.py, backend/src/agent/prompts.py)
- [X] T018 [US1] Complete chat route controller handling JWT auth, conversation lookup, message persistence, agent call, response payload (backend/src/routes/chat.py)
- [X] T019 [US1] Persist assistant messages + tool call metadata in conversation history (backend/src/services/conversation_service.py)
- [X] T020 [US1] Implement frontend chat API helper `sendChatMessage` hitting `/api/{user_id}/chat` (frontend/src/lib/api.ts)
- [X] T021 [US1] Build ChatKit/Tailwind chat page with composer, loading indicator, optimistic append, error toast (frontend/src/app/dashboard/chat/page.tsx)
- [X] T022 [US1] Store chat messages + pending state in Zustand store/shared hook (frontend/src/stores/chat-store.ts)
- [X] T023 [US1] Render task creation confirmations referencing task IDs in chat feed (frontend/src/app/dashboard/chat/page.tsx - renderToolCalls function)

**Checkpoint**: Natural language task creation works end-to-end.

---

## Phase 4: User Story 2 - Conversational Task Management (Priority: P2)

**Goal**: Users can list, update, complete, and delete tasks via chat.
**Independent Test**: Ask "What's pending?" then "I finished task 3"; verify list response and completion (spec.md:31-38).

### Tests
- [X] T024 [P] [US2] Contract test for listing + mutation intents through `/api/{user_id}/chat` (backend/tests/contract/test_chat_manage_tasks.py)
- [X] T025 [P] [US2] Integration test covering list → complete → edit flow (backend/tests/integration/test_chat_manage_tasks.py)
- [X] T026 [P] [US2] Frontend test verifying completed tasks render status updates in chat bubbles (frontend/tests/components/chat/chat-manage.test.tsx)

### Implementation
- [X] T027 [P] [US2] Implement MCP tools: `list_tasks(filter)`, `update_task(id, fields)`, `complete_task(id)`, `delete_task(id)` (backend/src/mcp_server.py - all CRUD tools implemented)
- [X] T028 [US2] Expand agent prompt + planner to clarify ambiguous references and require confirmations (backend/src/agent/prompts.py)
- [X] T029 [US2] Add bulk-destructive confirmation workflow returning `confirmation_required` flag (backend/src/routes/chat.py)
- [X] T030 [US2] Implement frontend confirmation modal component for "delete all" or ambiguous commands (frontend/src/components/chat/confirmation.tsx)
- [X] T031 [US2] Update chat page to handle tool call transcripts + status updates (frontend/src/app/dashboard/chat/page.tsx)
- [X] T032 [US2] Persist task status summaries in assistant responses for auditability (backend/src/services/conversation_service.py)
- [X] T033 [US2] Update Zustand store to reconcile server-confirmed task state with optimistic UI (frontend/src/stores/chat-store.ts)

**Checkpoint**: Full CRUD via conversation achieved.

---

## Phase 5: User Story 3 - Persistent Conversation Context (Priority: P3)

**Goal**: Chat history is saved and restored across sessions with sliding context window.
**Independent Test**: Send message, reload `/dashboard/chat`, verify history preserved and referenced (spec.md:47-52).

### Tests
- [X] T034 [P] [US3] Backend integration test ensuring messages fetched in order & limited to user (backend/tests/integration/test_chat_history.py)
- [X] T035 [P] [US3] Frontend E2E test (Playwright) validating history persists across reload (frontend/tests/e2e/chat-history.spec.ts)

### Implementation
- [X] T036 [P] [US3] Add conversation history GET endpoint (or extend chat POST) to return full history (backend/src/routes/chat.py - GET /history endpoint)
- [X] T037 [US3] Implement conversation repository query with pagination + sliding 20-message window for Gemini calls (backend/src/services/conversation_service.py)
- [X] T038 [US3] Update agent runner to inject latest 20 messages while keeping full history persisted (backend/src/agent/runner.py)
- [X] T039 [US3] Hydrate frontend chat store with server history on page load (frontend/src/stores/chat-store.ts - fetchHistory)
- [X] T040 [US3] Render persisted history in ChatKit components, scrolled to latest (frontend/src/app/dashboard/chat/page.tsx)
- [X] T041 [US3] Handle references like "Delete that task" by leveraging prior assistant messages (backend/src/agent/prompts.py)

**Checkpoint**: Conversation context survives reloads and informs follow-up commands.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T042 [P] Implement per-user rate limiting (30 req/min) using FastAPI dependency + 429 handling (backend/src/middleware/rate_limit.py + backend/src/routes/chat.py)
- [X] T043 [P] Add telemetry/logging for MCP tool calls + latency metrics (backend/src/agent/runner.py - structured logging added)
- [X] T044 Harden error states + retry guidance in chat UI (frontend/src/components/chat/chat-error.tsx)
- [X] T045 [P] Update documentation (plan.md + specs) with final architecture + confirmation flows (specs/001-ai-chatbot/plan.md)
- [X] T046 Run `quickstart.md` validation: start backend, MCP server, frontend, execute sample chat to confirm instructions (validate-quickstart.sh)

---

## Phase 7: Multiple Conversations Support (Missing Feature from Hackathon Requirements)

**Goal**: Allow users to start new conversations and manage multiple chat sessions, as referenced in the main hackathon requirements.

### Backend Implementation
- [X] T047 [P] Update conversation service to support multiple conversations per user (backend/src/services/conversation_service.py)
- [X] T048 [P] Add conversation management endpoints: POST /api/{user_id}/conversations (create), GET /api/{user_id}/conversations (list), DELETE /api/{user_id}/conversations/{id} (delete) (backend/src/routes/conversations.py)
- [ ] T049 [P] Update chat endpoints to accept conversation_id parameter and create new conversation if not provided (backend/src/routes/chat.py)

### Frontend Implementation  
- [X] T050 [P] Add conversation sidebar component with list of conversations and "New Chat" button (frontend/src/components/chat/conversation-sidebar.tsx)
- [X] T051 [P] Update chat store to manage multiple conversations and active conversation state (frontend/src/stores/chat-store.ts)
- [X] T052 [P] Update chat page layout to include conversation sidebar and conversation switching (frontend/src/app/dashboard/chat/page.tsx)
- [ ] T053 [P] Add conversation management actions: rename conversation, delete conversation (frontend/src/components/chat/conversation-actions.tsx)

### Database Schema Updates
- [X] T054 [P] Add conversation title field and update models (backend/src/models.py)
- [ ] T055 [P] Create migration for conversation title and indexes (backend/migrations/versions/*_conversation_title.py)

**Checkpoint**: Users can create multiple conversations, switch between them, and manage conversation history independently.

---

## Dependencies & Execution Order

1. **Phase 1** → 2 → 3 → 4 → 5 → 6 (sequential at phase level)
2. User stories unlock after Phase 2. Within a story, tests (T013/T014/T015 etc.) should be authored before implementation tasks.
3. Conversation service work (T005-T012) is prerequisite for all chat flows.
4. Frontend store/components (T022, T033, T039) depend on API helpers (T020) and backend endpoints (T018, T029, T036).
5. Polish tasks rely on completion of all user stories to avoid rework.

## Parallel Execution Examples

- After Phase 2, run T013–T015 (tests) in parallel while T016–T018 implement backend logic.
- In Phase 4, one developer can handle MCP tool expansions (T027) while another builds confirmations UI (T030) and another updates agent prompt (T028).
- Phase 5 allows backend history work (T036-T038) to proceed alongside frontend hydration/rendering (T039-T040).

## Implementation Strategy

1. Complete Phases 1-2 to establish environment, schema, services, and agent scaffolding.
2. Deliver MVP by finishing Phase 3 (US1) and validating independent test scenario.
3. Iterate with Phase 4 (US2) to unlock full conversational CRUD.
4. Add Phase 5 (US3) for persistent context + reload experience.
5. Apply Phase 6 polish for reliability, observability, and documentation updates.

MVP scope = Phases 1–3 (up through T023).
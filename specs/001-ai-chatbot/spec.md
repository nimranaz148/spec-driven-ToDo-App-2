# Feature Specification: AI-Powered Todo Chatbot - Phase 3

**Feature Branch**: `001-ai-chatbot`
**Created**: 2026-01-03
**Status**: Draft
**Input**: User description: "@spec-prompt-phase-3.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Task Creation (Priority: P1)

As a busy user, I want to create tasks by simply typing what I need to do in plain English, so that I can capture my todos quickly without navigating through complex forms.

**Why this priority**: Core value proposition of Phase 3. It allows users to immediately start using the AI for the most common action (adding tasks).

**Independent Test**: Can be fully tested by sending the message "Add a task to buy groceries" to the chatbot and verifying a confirmation response and the existence of the task in the list.

**Acceptance Scenarios**:

1. **Given** I am logged in and on the chat page, **When** I type "Remind me to call Mom at 5pm" and press send, **Then** the AI confirms it has added a task called "Call Mom at 5pm" and includes a unique task reference ID.
2. **Given** I am on the chat page, **When** I type "I need to buy milk, eggs, and bread", **Then** the system creates a single task with the title "Buy milk, eggs, and bread" and confirms the action.

---

### User Story 2 - Conversational Task Management (Priority: P2)

As a user, I want to view, update, and mark tasks as complete by talking to the assistant, so that I have a single conversational interface to manage my entire list.

**Why this priority**: Completes the CRUD cycle via natural language, making the chatbot a full replacement for the traditional UI.

**Independent Test**: Can be tested by asking "What's pending?" to see a list, then saying "I finished task 3" and verifying the task status changes.

**Acceptance Scenarios**:

1. **Given** I have 3 pending tasks, **When** I ask "What do I need to do?", **Then** the AI lists all 3 tasks with their respective IDs and status.
2. **Given** I have a task with ID 5, **When** I say "Mark task 5 as done", **Then** the system updates the task to completed and the AI responds with a success confirmation.
3. **Given** I have a task with a typo, **When** I say "Change task 1 to 'Pick up dry cleaning'", **Then** the task title is updated and confirmed.

---

### User Story 3 - Persistent Conversation Context (Priority: P3)

As a user, I want my chat history to be saved, so that I can see what I've previously discussed with the assistant and maintain context over multiple sessions.

**Why this priority**: Enhances usability and trust; users expect conversational tools to remember the recent history.

**Independent Test**: Can be tested by sending a message, navigating away from the chat page, returning, and verifying the message is still there.

**Acceptance Scenarios**:

1. **Given** I have sent messages today, **When** I refresh the page or log in later, **Then** all previous messages from the current conversation are displayed in order.
2. **Given** an ongoing conversation, **When** I send a follow-up like "Delete that task" (referring to a previously mentioned one), **Then** the AI uses the history to identify the correct task.

---

### Edge Cases

- **What happens when the user command is vague (e.g., "Delete my meeting task" when there are two meeting tasks)?**
  - The AI assistant must list the matches and ask for clarification instead of guessing or deleting both.
- **How does the system handle AI model latency or downtime?**
  - The UI must show a loading state while waiting; if the request fails, a friendly error message should suggest trying again.
- **What happens if a user tries to access a conversation ID that doesn't belong to them?**
  - The system must deny access and return a forbidden error based on JWT validation.
- **How are destructive bulk commands handled (e.g., "Delete all my tasks")?**
  - The assistant must trigger a secondary UI confirmation flow before executing any bulk delete/complete operations.

## Clarifications

### Session 2026-01-03

- Q: Which LLM provider/model should power the assistant? → A: Gemini via AsyncOpenAI (gemini-2.5-flash).
- Q: How should the chat UI be presented within the app? → A: Dedicated `/app/chat` page using the ChatKit layout with space for the sidebar.
- Q: How should long conversation histories be managed for context windows? → A: Use a sliding window of roughly the last 20 messages per LLM request while keeping full history persisted.
- Q: Which orchestration/library should wire the LLM to backend tools? → A: FastMCP with native MCP integration via `MCPServerStreamableHttp`, no LangChain wrapper.
- Q: Should bulk destructive commands require extra confirmation? → A: Yes—display a UI confirmation prompt before executing commands like "delete all".

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a conversational interface where users can send text messages and receive AI-generated responses.
- **FR-002**: System MUST process natural language inputs to perform task operations: create, read (list), update, complete, and delete.
- **FR-003**: System MUST identify the user from their session token and ensure they only interact with their own tasks and conversations.
- **FR-004**: System MUST persist every message (both user and assistant) in a database associated with a specific conversation.
- **FR-005**: AI Assistant MUST confirm every destructive or state-changing action (create, update, delete, complete) with a clear success message.
- **FR-006**: System MUST handle "list" requests with filters (e.g., "show pending", "show completed") using natural language.
- **FR-007**: System MUST provide a loading indicator in the UI while the AI is processing a message.

### Key Entities *(include if feature involves data)*

- **Conversation**: Represents a unique chat session. Attributes include `id`, `user_id`, and timestamps.
- **Message**: A single unit of communication within a conversation. Attributes include `id`, `conversation_id`, `user_id`, `role` (user/assistant), `content`, and `created_at`.
- **Task**: The existing todo entity. The chatbot interacts with this via tool calls to manage title, description, and status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete a task-related action (Add/Complete/List) using natural language in under 5 seconds (from send click to response).
- **SC-002**: 90% of standard task commands (as defined in examples) are correctly interpreted and executed by the AI on the first attempt.
- **SC-003**: 100% of user messages and AI responses are successfully persisted and retrievable upon page reload.
- **SC-004**: Zero instances of "cross-talk" where User A can see or modify User B's tasks or chat history.
- **SC-005**: The chat interface remains responsive and usable on mobile devices (portrait view).

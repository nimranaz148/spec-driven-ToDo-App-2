# Data Model — AI-Powered Todo Chatbot

## Entities

### Conversation
| Field | Type | Notes |
|-------|------|-------|
| id | integer (PK) | Auto-increment primary key |
| user_id | string | Owner (Better Auth user id); indexed to enforce isolation |
| created_at | datetime | Defaults to `datetime.utcnow()` |
| updated_at | datetime | Updated on every message append |

**Relationships**: 1 Conversation → many Messages. Conversations never cross users.

**Validation rules**:
- `user_id` required and must match JWT subject.
- Only one active conversation per user for Phase 3 (future phases can relax).

### Message
| Field | Type | Notes |
|-------|------|-------|
| id | integer (PK) | Auto-increment |
| user_id | string | Redundant owner column for fast filtering (matches Conversation user) |
| conversation_id | integer (FK) | References `conversations.id`, cascades delete |
| role | enum("user", "assistant") | Ensures downstream UI can render styles |
| content | text | Full message body (validated <= 4000 chars) |
| created_at | datetime | Defaults to UTC |

**Relationships**: Belongs to Conversation. Messages are ordered by `created_at, id`.

**Validation rules**:
- `content` must be non-empty and <= 4000 characters.
- `role` limited to "user" or "assistant" (system prompts out-of-scope in Phase 3).

### Task (existing)
Reuse current Task model (`backend/src/models.py`). The MCP server and agent will call CRUD operations through SQLModel/TaskService; no schema changes this phase.

## State & Transitions

```
Conversation (user creates first message)
  └── Message(role="user") added
        ├── Agent call
        └── Message(role="assistant") persisted
```

- Conversations are created lazily on first chat request.
- Messages append in chronological order; updates are not supported (immutable history).
- Deleting a conversation cascades to all messages (not exposed in Phase 3 UI, but enforced in DB).

## Indexing & Performance

- `conversations.user_id` — supports fast lookup by authenticated user.
- `messages.conversation_id` — fetch message history quickly.
- `messages.user_id` — ensures user isolation in multi-tenant queries.

## Derived Views

- Chat history API sorts messages by `created_at ASC`, limited to entire history (Phase 3 requirement). Context window trimming happens server-side before calling Gemini.

---

## Implementation Status

### Database Models (Implemented)
- **Location**: `backend/src/models.py`
- **Entities**: `Task`, `Conversation`, `Message`, `MessageRole` enum
- **Relationships**: Conversation → Messages (one-to-many with cascade delete)

### Migration
- **Location**: `backend/migrations/versions/20260104_0001_add_conversation_message.py`
- Creates `conversations` and `messages` tables with proper indexes and FK constraints

### Services
- **ConversationService**: `backend/src/services/conversation_service.py`
  - `get_or_create_conversation(user_id)` - Lazy conversation creation
  - `append_message(conversation, role, content)` - Add message to history
  - `list_recent_messages(conversation_id, user_id, limit=20)` - Sliding window for LLM
  - `get_full_history(conversation_id, user_id)` - Complete history for UI

---

## MCP Components

### Official MCP Server
- **Location**: `backend/src/mcp_server.py`
- **Purpose**: Expose task CRUD operations as tools for the AI agent
- **Transport**: HTTP via FastMCP

### Available Tools
| Tool | Parameters | Description |
|------|------------|-------------|
| `create_task` | `title`, `description?` | Create a new task |
| `list_tasks` | `completed?` | List user's tasks with optional filter |
| `update_task` | `task_id`, `title?`, `description?` | Update existing task |
| `complete_task` | `task_id` | Mark task as completed |
| `delete_task` | `task_id` | Delete a task |

### Agent Configuration
- **Location**: `backend/src/agent/config.py`
- **LLM**: Gemini 2.5 Flash via AsyncOpenAI transport
- **Fallback**: LiteLLM for alternative transport

# Phase 0 Research — AI-Powered Todo Chatbot

## Decision 1: Gemini 2.5 Flash via AsyncOpenAI transport
- **Decision**: Use Gemini 2.5 Flash (gemini-2.5-flash) through the AsyncOpenAI-compatible transport so the Agents SDK can talk to Gemini with LiteLLM as a fallback shim.
- **Rationale**: The spec explicitly calls for Gemini via AsyncOpenAI and a 5-second round-trip requirement (SC-001), so a fast multimodal Gemini tier is needed (`specs/001-ai-chatbot/spec.md:69-104`). AsyncOpenAI keeps compatibility with OpenAI-style clients while letting us supply the Gemini API key once.
- **Alternatives considered**: Using OpenAI GPT-4o directly (rejected: violates requirement to showcase Gemini). Calling Gemini’s native REST API without AsyncOpenAI/FastMCP (rejected: more glue code and loses Agents SDK tooling).

## Decision 2: Official MCP server + FastMCP bridge
- **Decision**: Build an Official MCP SDK server that exposes add/list/update/complete/delete task tools and connect it to the agent runner with FastMCP (`specs/001-ai-chatbot/spec.md:71-76`).
- **Rationale**: MCP tooling keeps each task mutation auditable, and FastMCP’s `MCPServerStreamableHttp` removes the need for LangChain or custom function-call plumbing. It also lets us reuse the MCP server independently for future agents.
- **Alternatives considered**: Direct database calls from the agent code (rejected: mixes orchestration and persistence, harder to test). LangChain Tools (rejected: spec explicitly forbids LangChain for this phase).

## Decision 3: ChatKit-first UI with Tailwind fallback
- **Decision**: Attempt to use OpenAI ChatKit for 90% of the chat UI, but maintain a Tailwind-based custom fallback for parity (`specs/001-ai-chatbot/spec.md:711-889`).
- **Rationale**: ChatKit gives us polished message bubbles, typing indicators, and accessibility defaults. If the package is unavailable, the fallback ensures the chat page still meets SC-003/SC-005 without blocking delivery.
- **Alternatives considered**: Building the entire UI from scratch (rejected: longer build time, less polish). Using other UI kits like Stream Chat (rejected: spec wants ChatKit/Tailwind only).

## Decision 4: Single persistent conversation per user with sliding context window
- **Decision**: Persist every message in `conversations`/`messages` tables but send only the latest ~20 messages to Gemini on each call (`specs/001-ai-chatbot/spec.md:41-76`).
- **Rationale**: Full history satisfies SC-003 and lets the user reload the page, while the sliding window keeps prompt size manageable and avoids Gemini token bloat.
- **Alternatives considered**: Streaming the full history on every request (rejected: unnecessary token usage). Multiple conversations with sidebar management (rejected: explicitly out of scope for Phase 3).

## Decision 5: Guardrails for ambiguous or destructive commands
- **Decision**: When instructions are vague (duplicate “meeting” tasks) the agent must clarify; destructive bulk operations require a UI confirmation before calling MCP tools (`specs/001-ai-chatbot/spec.md:56-66`). Add optional rate limiting at 30 requests/minute per user.
- **Rationale**: Prevents accidental data loss and aligns with the edge-case expectations plus SC-004 isolation. Rate limiting mitigates runaway loops or accidental spam.
- **Alternatives considered**: Blindly executing ambiguous deletes (rejected: risks deleting wrong tasks). Skipping rate limiting (rejected: spec labels it “recommended,” so we capture it now to avoid rework later).

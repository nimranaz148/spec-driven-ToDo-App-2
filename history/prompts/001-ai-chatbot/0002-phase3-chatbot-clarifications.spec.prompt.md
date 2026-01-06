---
id: "0002"
title: "Phase3 chatbot clarifications"
stage: "spec"
date: "2026-01-03"
surface: "agent"
model: "claude-opus-4-5-20251101"
feature: "001-ai-chatbot"
branch: "001-ai-chatbot"
user: "maneeshanif"
command: "/sp.clarify"
labels: ["spec","clarification","ai-chatbot"]
links:
  spec: "specs/001-ai-chatbot/spec.md"
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-ai-chatbot/spec.md
tests:
  - n/a
---

## Prompt

Here are the clarified answers, aligned with the Gemini + native MCP setup from the openai-agents-setup skill:

  Q1: Gemini via AsyncOpenAI – Phase 3 architecture already standardizes on Gemini (gemini‑2.5‑flash) through AsyncOpenAI; this meets the spec’s latency/downtime requirements while keeping a consistent SDK surface.

  Q2: Standalone chat page – A dedicated /app/chat page gives ChatKit the space it needs for the full conversation layout plus sidebar, matching the Phase 3 UX plan.

  Q3: Sliding window (last ~20 messages) – Keeps recent intent context without unbounded token growth, aligning with the spec’s cost-control and memory requirements for continuous conversations.

  Q4: FastMCP with native MCP integration – Direct FastMCP tools plus MCPServerStreamableHttp (no LangChain wrappers) matches the documented architecture and minimizes maintenance.

  Q5: UI confirmation required – Destructive “delete all” flows should trigger a secondary UI confirmation, as the spec explicitly calls for extra safety around bulk actions.

## Response snapshot

Captured all five clarifications, updated the Edge Cases section with the bulk-delete confirmation rule, and added a new Clarifications section documenting the agreed LLM stack, chat layout, sliding window policy, FastMCP orchestration, and destructive-action safeguards. Spec now reflects the Phase 3 architecture decisions, unblocking /sp.plan.

## Outcome

- ✅ Impact: Clarified critical architectural and UX choices for Phase 3 chatbot
- 🧪 Tests: n/a (spec clarification)
- 📁 Files: specs/001-ai-chatbot/spec.md
- 🔁 Next prompts: /sp.plan
- 🧠 Reflection: Clarifications encoded directly in the spec reduce planning uncertainty and future rework.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): n/a
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Proceed to planning

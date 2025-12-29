# Todo App - Hackathon II

## Project Overview
This is a monorepo using GitHub Spec-Kit for spec-driven development.

## Spec-Kit Structure
Specifications are organized in /specs:
- /specs/overview.md - Project overview
- /specs/features/ - Feature specs (what to build)
- /specs/api/ - API endpoint specs
- /specs/database/ - Schema and model specs
- /specs/ui/ - Component and page specs

## How to Use Specs
1. Always read relevant spec before implementing
2. Reference specs with: @specs/features/file.md
3. Update specs if requirements change

## Project Structure
- /frontend - Next.js 16+ app (@frontend/CLAUDE.md)
- /backend - Python FastAPI server (@backend/CLAUDE.md)

## Development Workflow
1. Read spec: @specs/features/[feature].md
2. Implement backend: @backend/CLAUDE.md
3. Implement frontend: @frontend/CLAUDE.md
4. Test and iterate

## Library Documentation (Context 7 MCP)
Use the Context 7 MCP server for up-to-date library documentation:

**Context 7 MCP Configuration:**
- Type: HTTP Transport
- URL: `https://mcp.context7.com/mcp`
- API Key: Configured in user settings (ctx7sk-...)

**Key libraries with Context 7 docs:**
- FastAPI: `context7://fastapi/latest`
- SQLModel: `context7://sqlmodel/latest`
- Next.js: `context7://nextjs/latest`
- Tailwind CSS: `context7://tailwindcss/latest`
- Better Auth: `context7://better-auth/latest`
- Pydantic: `context7://pydantic/latest`

**When implementing, use Context 7:**
- "Fetch Context 7 docs for FastAPI dependency injection patterns"
- "Get Next.js 16 App Router server component best practices"
- "Use Context 7 for SQLModel relationship patterns"

**Verified working in this project.**

## Commands
- Frontend: cd frontend && npm run dev
- Backend: cd backend && uvicorn main:app --reload --port 8000
- Both: docker-compose up

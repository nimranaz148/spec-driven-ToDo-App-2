# Frontend Guidelines

## Stack
- Next.js 16+ (App Router)
- TypeScript
- Tailwind CSS
- Better Auth

## Coupling
- Part of monorepo: @CLAUDE.md (root)
- Backend counterpart: @backend/CLAUDE.md
- Specs: @specs/features/task-crud.md, @specs/features/authentication.md

## Patterns
- Use server components by default
- Client components only when needed (interactivity)
- API calls go through `/lib/api.ts`

## Component Structure
- `/components` - Reusable UI components
- `/app` - Pages and layouts
- `/lib` - Utilities and API client

## API Client
All backend calls should use the API client with JWT auth:

```typescript
import { api } from '@/lib/api'
const tasks = await api.getTasks()
```

## Better Auth Setup
- Configure JWT plugin for token generation
- Attach token to every API request header

## Library Documentation (Context 7 MCP)
**ALWAYS** use Context 7 MCP for up-to-date library docs:

**Context 7 HTTP Transport:**
- URL: `https://mcp.context7.com/mcp`
- API Key: Configured at user level (ctx7sk-...)

**Available libraries:**
- Next.js: `context7://nextjs/latest`
- Tailwind CSS: `context7://tailwindcss/latest`
- Better Auth: `context7://better-auth/latest`
- TypeScript: `context7://typescript/latest`

**When implementing frontend:**
1. Fetch Next.js patterns: "Use Context 7 to get Next.js App Router server component patterns"
2. Fetch Tailwind patterns: "Fetch Context 7 docs for Tailwind CSS best practices"
3. Fetch Better Auth: "Get Better Auth JWT plugin configuration from Context 7"

**Example prompt:**
> "Fetch Context 7 documentation for Next.js 16 App Router server actions and Form components"

## Styling
- Use Tailwind CSS classes
- No inline styles
- Follow existing component patterns

## Key Files
- `app/page.tsx` - Main dashboard
- `app/auth/*` - Authentication pages
- `components/TaskList.tsx` - Task display
- `components/TaskForm.tsx` - Task creation
- `lib/api.ts` - API client with auth

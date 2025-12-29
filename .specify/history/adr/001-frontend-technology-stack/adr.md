# ADR-001: Frontend Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-26
- **Feature:** Todo Web Application
- **Context:** Building a modern, responsive frontend for the todo application requires selecting a coordinated stack of technologies that work well together, provide excellent developer experience, and support production deployment.

## Decision

- **Framework:** Next.js 16+ (App Router)
- **Styling:** Tailwind CSS 4.0
- **Component Library:** Shadcn/ui (Radix UI primitives)
- **State Management:** Zustand 5.0+ (MANDATORY - no React Context)
- **HTTP Client:** Axios 1.7+ (MANDATORY - no fetch API)
- **Authentication:** Better Auth 1.0+ (JWT plugin)
- **Animations:** Framer Motion 11+
- **Forms:** React Hook Form + Zod
- **Deployment:** Vercel Edge Network

## Consequences

### Positive

- **Integrated DX:** Next.js + Tailwind + Vercel provides seamless development-to-deployment pipeline with minimal configuration
- **TypeScript support:** Excellent type inference across the full stack
- **State management:** Zustand provides simple, performant global state without Context overhead
- **HTTP client:** Axios provides interceptors, automatic JSON transformation, and consistent error handling
- **UI consistency:** Shadcn/ui offers accessible, customizable components built on Radix primitives
- **Animation:** Framer Motion enables smooth, declarative animations for polished UX
- **Form handling:** React Hook Form + Zod provides type-safe form validation

### Negative

- **Vendor lock-in:** Strong coupling to Vercel platform for optimal deployment
- **Learning curve:** Multiple libraries require understanding their interaction patterns
- **Bundle size:** Combining Shadcn/ui, Framer Motion, and Axios increases initial bundle size
- **Client-side state:** Zustand requires careful architecture to avoid over-fetching

## Alternatives Considered

**Alternative Stack A: Remix + styled-components + Cloudflare**
- Rejected: Remix's data loading patterns differ significantly from Next.js App Router, requiring different mental model
- More complex setup for styled-components compared to Tailwind's utility-first approach
- Cloudflare deployment less mature than Vercel for Next.js

**Alternative Stack B: Vite + vanilla CSS + AWS Amplify**
- Rejected: Requires more boilerplate for routing, SSR, and deployment
- Amplify's learning curve exceeds Vercel's zero-config deployment
- No SSR capability without additional configuration

## References

- Feature Spec: [specs/features/1-todo-web-app/spec.md](../specs/features/1-todo-web-app/spec.md)
- Implementation Plan: [specs/1-todo-web-app/plan.md](../specs/1-todo-web-app/plan.md)
- Data Model: [specs/1-todo-web-app/data-model.md](../specs/1-todo-web-app/data-model.md)
- Frontend Guidelines: [frontend/CLAUDE.md](../frontend/CLAUDE.md)

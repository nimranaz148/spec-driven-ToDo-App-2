# ADR-003: Database & ORM Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-26
- **Feature:** Todo Web Application
- **Context:** The database layer must provide reliable persistence, type-safe access patterns, and support for the multi-user isolation requirements defined in the feature specification.

## Decision

- **Database:** PostgreSQL (Neon Serverless - US region)
- **ORM:** SQLModel 0.0.24+
- **Connection:** Async connection pooling via SQLModel
- **Schema Management:** SQLModel auto-migrate
- **User Isolation:** Foreign key relationships with indexed user_id filtering

## Consequences

### Positive

- **Type safety:** SQLModel bridges SQLModel and Pydantic, providing unified type definitions
- **PostgreSQL power:** Full relational capabilities with JSON support, indexes, and transactions
- **Serverless scaling:** Neon provides automatic scaling without infrastructure management
- **Async support:** Native async driver support for high-concurrency scenarios
- **Simple migrations:** Auto-migrate handles schema changes during development
- **Data isolation:** Foreign key + indexed user_id ensures secure multi-user access

### Negative

- **Migration complexity:** Auto-migrate not suitable for production schema changes
- **Neon cold starts:** Serverless functions may experience connection latency
- **Vendor dependency:** Neon-specific features may not port to self-hosted PostgreSQL
- **Connection limits:** Serverless tier has connection pool limits requiring careful management

## Alternatives Considered

**Alternative Stack A: SQLite + SQLAlchemy**
- Rejected: No multi-user production capability, connection locking issues
- Neon PostgreSQL required for Vercel deployment compatibility

**Alternative Stack B: MongoDB + Mongoose**
- Rejected: No relational integrity for user-task relationships
- Less familiar for team with SQL background
- No equivalent to SQLModel's type unification

**Alternative Stack C: PostgreSQL + Prisma (Node.js)**
- Rejected: Would require separate backend, breaking monorepo cohesion
- Python team expertise favors SQLModel

**Alternative Stack D: PostgreSQL + raw SQL + psycopg**
- Rejected: No type safety, manual schema management, higher bug risk

## References

- Feature Spec: [specs/features/1-todo-web-app/spec.md](../specs/features/1-todo-web-app/spec.md)
- Implementation Plan: [specs/1-todo-web-app/plan.md](../specs/1-todo-web-app/plan.md)
- Data Model: [specs/1-todo-web-app/data-model.md](../specs/1-todo-web-app/data-model.md)
- API Endpoints: [specs/api/endpoints.md](../specs/api/endpoints.md)

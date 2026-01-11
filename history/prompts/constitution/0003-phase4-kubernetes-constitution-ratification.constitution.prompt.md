---
id: 0003
title: Phase 4 Kubernetes Constitution Ratification
stage: constitution
date: 2026-01-12
surface: agent
model: claude-sonnet-4.5
feature: none
branch: main
user: USER
command: /speckit.constitution @constitution-prompt-phase-4.md
labels: ["constitution", "phase-4", "kubernetes", "docker", "helm"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - constitution-prompt-phase-4.md
tests:
  - none
---

## Prompt

/speckit.constitution @constitution-prompt-phase-4.md

## Response snapshot

Updated project constitution from Phase 3 (Todo Chatbot) to Phase 4 (Local Kubernetes Deployment). The constitution now defines:

**Core Principles (8 NON-NEGOTIABLE + 1 ENCOURAGED)**:

1. Infrastructure as Code - All K8s manifests version-controlled
2. Multi-Stage Builds - Minimize Docker image sizes
3. Resource Limits - CPU/memory requests and limits for all containers
4. Health Probes - Liveness and readiness probes required
5. Service Discovery - Use Kubernetes DNS, not localhost
6. Secrets Management - Never hardcode credentials
7. Immutable Infrastructure - Deploy via code, no manual edits
8. AIOps Integration - Use Docker AI, kubectl-ai, Kagent

**Technology Stack**:

- Containers: node:20-alpine (frontend), python:3.13-slim (backend/mcp)
- Orchestration: Minikube, kubectl, Docker
- Package Management: Helm charts
- AIOps: Docker AI (Gordon), kubectl-ai, Kagent

**Architecture**:

- Frontend (2 replicas, 3000), Backend (2 replicas, 8000), MCP Server (1 replica, 8001)
- External DB: Neon PostgreSQL
- Service Discovery: Internal ClusterIP services
- External Access: Ingress at todo.local

**Development Workflow**:

1. Dockerize (Dockerfiles + docker-compose)
2. Create K8s manifests (namespace, deployments, services, ingress)
3. Helm chart creation (optional but recommended)
4. Prepare for Phase 5 (Dapr annotations, Kafka topics)

**Deliverables**:

- Dockerfiles for 3 services
- docker-compose.yml
- K8s manifests in k8s/ (9 files)
- Helm chart in helm/todo-app/
- Documentation (README, setup guides)

**Phase 5 Prep**:

- Dapr annotations (disabled for Phase 4)
- Kafka topic planning (task-events, reminders, task-updates)
- Cloud registry selection (GHCR, Docker Hub, DOKS)

## Outcome

- ✅ Impact: Constitution updated with comprehensive Phase 4 Kubernetes deployment principles and standards
- 🧪 Tests: None required for constitution updates
- 📁 Files: Updated .specify/memory/constitution.md
- 🔁 Next prompts: /sp.spec for feature specification, /sp.plan for architecture planning
- 🧠 Reflection: Phase 4 focuses on containerization and local K8s deployment as foundation for Phase 5 production deployment

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (constitution update)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin Phase 4 implementation with Docker containerization

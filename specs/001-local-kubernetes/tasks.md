# Implementation Tasks: Local Kubernetes Deployment

**Feature**: 001-local-kubernetes  
**Branch**: `001-local-kubernetes`  
**Date**: 2026-01-12  
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Overview

This document breaks down the implementation of Phase 4 Local Kubernetes Deployment into atomic, testable tasks organized by user story. Each user story represents an independently deployable increment.

**Total Tasks**: 32  
**Parallelization Opportunities**: 15 tasks marked [P]

---

## Phase 1: Setup & Prerequisites

**Goal**: Prepare repository structure and tooling for Kubernetes deployment

- [x] T001 Create k8s/ directory in repository root
- [x] T002 Create helm/todo-app/ directory with standard Helm chart structure
- [x] T003 Create mcp/ directory for MCP Server deployment artifacts
- [x] T004 Add .dockerignore files to backend/, frontend/, and mcp/ directories
- [x] T005 Update .gitignore to exclude k8s/secrets.yaml and Helm packaged charts
- [x] T006 Document prerequisites in README.md (Docker Desktop, Minikube, Helm, kubectl)

**Validation**: Directories exist, .dockerignore files prevent unnecessary context, secrets excluded from git

---

## Phase 2: Foundational Infrastructure

**Goal**: Create shared Kubernetes resources required by all services

- [x] T007 Create k8s/namespace.yaml for todo-app namespace
- [x] T008 Create k8s/configmap.yaml with BACKEND_URL, MCP_SERVER_URL, NODE_ENV, LOG_LEVEL
- [x] T009 Create k8s/secrets.yaml.template with placeholders for DATABASE_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL, OPENAI_API_KEY
- [x] T010 Create deployment documentation in specs/001-local-kubernetes/quickstart.md with step-by-step instructions

**Validation**: Manifests apply successfully, ConfigMap and Secret (from template) exist in todo-app namespace

---

## Phase 3: User Story 1 - Containerize Applications (P1)

**Goal**: Create optimized Docker images for all three services using multi-stage builds

**Independent Test**: Can build all 3 images locally using docker build commands and verify sizes (Frontend <200MB, Backend <500MB)

### Backend Dockerfile

- [x] T011 [P] [US1] Create backend/Dockerfile with multi-stage build (Python 3.11-slim builder and runtime)
- [x] T012 [P] [US1] Add non-root user (appuser, uid 1000) in backend/Dockerfile
- [x] T013 [P] [US1] Configure backend/Dockerfile to copy pyproject.toml, install dependencies, then copy source
- [x] T014 [P] [US1] Set backend/Dockerfile runtime CMD to run uvicorn on port 8000
- [x] T015 [P] [US1] Create backend/.dockerignore excluding tests/, **pycache**/, .env

### Frontend Dockerfile

- [x] T016 [P] [US1] Create frontend/Dockerfile with multi-stage build (Node 20 deps, builder, Alpine runtime)
- [x] T017 [P] [US1] Add non-root user (appuser, uid 1000) in frontend/Dockerfile
- [x] T018 [P] [US1] Configure frontend/Dockerfile to run npm ci, build, and copy artifacts to runtime
- [x] T019 [P] [US1] Set frontend/Dockerfile runtime CMD to run npm start on port 3000
- [x] T020 [P] [US1] Create frontend/.dockerignore excluding node_modules/, .next/, tests/

### MCP Server Dockerfile

- [x] T021 [P] [US1] Create mcp/Dockerfile with multi-stage build (Python 3.11-slim, reuses backend code)
- [x] T022 [P] [US1] Add non-root user (appuser, uid 1000) in mcp/Dockerfile
- [x] T023 [P] [US1] Configure mcp/Dockerfile to install backend dependencies and copy mcp_server.py
- [x] T024 [P] [US1] Set mcp/Dockerfile runtime CMD to run python -m src.mcp_server on port 8001

### Validation & Documentation

- [x] T025 [US1] Create docker-compose.yml for local testing with all three services
- [ ] T026 [US1] Test image builds with eval $(minikube docker-env) and verify sizes meet SC-003
- [x] T027 [US1] Document build instructions in specs/001-local-kubernetes/quickstart.md

**Acceptance**:

- ✅ All images build successfully
- ✅ Frontend image < 200MB (uncompressed)
- ✅ Backend image < 500MB (uncompressed)
- ✅ All containers run as non-root users (FR-002)
- ✅ docker-compose up runs all services locally

---

## Phase 4: User Story 2 - Deploy Core Infrastructure & Backend Services (P2)

**Goal**: Deploy Backend and MCP Server to Minikube with proper configuration

**Independent Test**: Can access Backend /health endpoint from within cluster and Backend can reach MCP Server

### Backend Kubernetes Resources

- [x] T028 [P] [US2] Create k8s/backend-deployment.yaml with 2 replicas, resource limits (512Mi/1 CPU), init container for Alembic migrations
- [x] T029 [P] [US2] Add liveness/readiness probes to backend-deployment.yaml (HTTP GET /health on port 8000)
- [x] T030 [P] [US2] Configure backend-deployment.yaml to mount ConfigMap and Secret as environment variables
- [x] T031 [P] [US2] Create k8s/backend-service.yaml as ClusterIP on port 8000

### MCP Server Kubernetes Resources

- [x] T032 [P] [US2] Create k8s/mcp-deployment.yaml with 1 replica, resource limits (256Mi/0.5 CPU)
- [x] T033 [P] [US2] Add liveness/readiness probes to mcp-deployment.yaml (HTTP GET /health on port 8001)
- [x] T034 [P] [US2] Configure mcp-deployment.yaml to mount ConfigMap and Secret as environment variables
- [x] T035 [P] [US2] Create k8s/mcp-service.yaml as ClusterIP on port 8001

### Deployment & Validation

- [x] T036 [US2] Create deployment script scripts/deploy-backend.sh (build images, apply manifests)
- [ ] T037 [US2] Test Backend deployment: verify pods Running, check logs for successful DB connection
- [ ] T038 [US2] Test Backend health endpoint: kubectl port-forward and curl http://localhost:8000/health
- [ ] T039 [US2] Test Backend -> MCP connectivity: kubectl exec into backend pod, curl http://mcp-server:8001/health

**Acceptance**:

- ✅ Backend and MCP pods show "Running" status (SC-002)
- ✅ Init container runs migrations successfully (FR-012)
- ✅ Backend /health returns 200 OK
- ✅ Backend can reach MCP Server on http://mcp-server:8001 (FR-006)
- ✅ No database connection errors in Backend logs

---

## Phase 5: User Story 3 - Enable Frontend Access (P3)

**Goal**: Deploy Frontend and expose via Ingress on todo.local

**Independent Test**: Can open http://todo.local in browser and interact with the app

### Frontend Kubernetes Resources

- [ ] T040 [P] [US3] Create k8s/frontend-deployment.yaml with 2 replicas, resource limits (256Mi/0.5 CPU)
- [ ] T041 [P] [US3] Add liveness/readiness probes to frontend-deployment.yaml (HTTP GET /\_next/health on port 3000)
- [ ] T042 [P] [US3] Configure frontend-deployment.yaml with NEXT_PUBLIC_BACKEND_URL environment variable
- [ ] T043 [P] [US3] Create k8s/frontend-service.yaml as ClusterIP on port 3000

### Ingress Configuration

- [ ] T044 [US3] Create k8s/ingress.yaml with NGINX ingressClassName and host todo.local
- [ ] T045 [US3] Configure ingress.yaml with two paths: / → frontend-service:3000, /api → backend-service:8000
- [ ] T046 [US3] Add NGINX Ingress Controller enable step to deployment script (minikube addons enable ingress)
- [ ] T047 [US3] Add /etc/hosts entry instructions to quickstart.md (127.0.0.1 todo.local or minikube ip)

### Deployment & Validation

- [ ] T048 [US3] Update deployment script to include Frontend resources
- [ ] T049 [US3] Test Frontend deployment: verify pods Running with 2 replicas
- [ ] T050 [US3] Test Ingress: curl http://todo.local should return HTML (SC-004)
- [ ] T051 [US3] Test end-to-end flow: open http://todo.local in browser, login, create a task, verify in DB

**Acceptance**:

- ✅ Frontend pods show "Running" status with 2 replicas (FR-007)
- ✅ Ingress routes traffic to Frontend on todo.local
- ✅ Application responds with 200 OK (SC-004)
- ✅ Full stack communication: Frontend → Backend → MCP → Neon DB works
- ✅ User can interact with Todo Chatbot UI

---

## Phase 6: User Story 4 - Operational Optimization (P4)

**Goal**: Package deployment as Helm chart and enable AI-assisted operations

**Independent Test**: Can deploy entire stack using helm install and query status with kubectl-ai

### Helm Chart Creation

- [ ] T052 [P] [US4] Create helm/todo-app/Chart.yaml with chart metadata (name, version 0.1.0, apiVersion v2)
- [ ] T053 [P] [US4] Create helm/todo-app/values.yaml with all configurable parameters (replicas, resources, images, ingress)
- [ ] T054 [P] [US4] Create helm/todo-app/values-dev.yaml with dev-specific overrides (imagePullPolicy: Never)
- [ ] T055 [P] [US4] Create helm/todo-app/templates/\_helpers.tpl with label and name helpers

### Helm Templates

- [ ] T056 [P] [US4] Convert k8s/namespace.yaml to helm/todo-app/templates/namespace.yaml with values templating
- [ ] T057 [P] [US4] Convert k8s/configmap.yaml to helm/todo-app/templates/configmap.yaml with values templating
- [ ] T058 [P] [US4] Convert k8s/secrets.yaml.template to helm/todo-app/templates/secrets.yaml with values templating
- [ ] T059 [P] [US4] Convert k8s/backend-deployment.yaml to helm/todo-app/templates/backend-deployment.yaml with values templating
- [ ] T060 [P] [US4] Convert k8s/backend-service.yaml to helm/todo-app/templates/backend-service.yaml with values templating
- [ ] T061 [P] [US4] Convert k8s/mcp-deployment.yaml to helm/todo-app/templates/mcp-deployment.yaml with values templating
- [ ] T062 [P] [US4] Convert k8s/mcp-service.yaml to helm/todo-app/templates/mcp-service.yaml with values templating
- [ ] T063 [P] [US4] Convert k8s/frontend-deployment.yaml to helm/todo-app/templates/frontend-deployment.yaml with values templating
- [ ] T064 [P] [US4] Convert k8s/frontend-service.yaml to helm/todo-app/templates/frontend-service.yaml with values templating
- [ ] T065 [P] [US4] Convert k8s/ingress.yaml to helm/todo-app/templates/ingress.yaml with values templating

### Validation & Documentation

- [ ] T066 [US4] Run helm lint ./helm/todo-app and fix any errors (SC-005)
- [ ] T067 [US4] Create helm/todo-app/README.md with installation instructions and value descriptions
- [ ] T068 [US4] Test Helm deployment: helm install todo-app ./helm/todo-app --set secrets.databaseUrl=$DATABASE_URL
- [ ] T069 [US4] Verify Helm deployment matches manual deployment (all pods Running, services accessible)
- [ ] T070 [US4] Document kubectl-ai usage examples in specs/001-local-kubernetes/quickstart.md
- [ ] T071 [US4] Document kagent setup and usage in specs/001-local-kubernetes/quickstart.md

**Acceptance**:

- ✅ Helm chart passes helm lint with 0 errors (SC-005, FR-10)
- ✅ helm install deploys entire stack successfully
- ✅ Helm deployment is functionally equivalent to raw manifests
- ✅ kubectl-ai can answer troubleshooting queries (FR-11)
- ✅ Documentation includes operational tooling guides

---

## Phase 7: Polish & Validation

**Goal**: Finalize documentation, add validation scripts, ensure all success criteria met

- [ ] T072 Create scripts/validate-deployment.sh to check all pods Running, services ready, ingress accessible
- [ ] T073 Add deployment timing measurements to validate SC-001 (<5 minute deployment)
- [ ] T074 Create scripts/teardown.sh to clean up Minikube resources (kubectl delete namespace todo-app)
- [ ] T075 Update root README.md with Phase 4 deployment instructions and links to quickstart
- [ ] T076 Add troubleshooting section to specs/001-local-kubernetes/quickstart.md (common issues, solutions)
- [ ] T077 Create Makefile with targets: build-images, deploy-k8s, deploy-helm, validate, teardown
- [ ] T078 Run full validation: measure deployment time, verify image sizes, check pod stability (5 min, 0 restarts)
- [ ] T079 Document Gordon (Docker Desktop AI) usage for Dockerfile optimization in specs/001-local-kubernetes/quickstart.md

**Acceptance**:

- ✅ All success criteria validated (SC-001 through SC-005)
- ✅ Deployment completes in <5 minutes (SC-001)
- ✅ All pods stable with 0 restarts after 5 minutes (SC-002)
- ✅ Image sizes meet constraints (SC-003)
- ✅ Application accessible and functional (SC-004)
- ✅ Documentation is comprehensive and accurate

---

## Dependencies & Execution Order

### User Story Dependencies

```
Setup (Phase 1)
  ↓
Foundational (Phase 2)
  ↓
US1: Containerize (Phase 3) - BLOCKING all others
  ↓
  ├─→ US2: Backend Services (Phase 4) - BLOCKING US3
  │     ↓
  └──→ US3: Frontend Access (Phase 5)
        ↓
US4: Helm & Operations (Phase 6) - DEPENDS ON US1, US2, US3
  ↓
Polish (Phase 7)
```

### Parallel Execution Opportunities

**Within US1 (Dockerfiles)**: T011-T024 can all be done in parallel (different files)

**Within US2 (Backend/MCP K8s)**: T028-T035 can all be done in parallel (different manifests)

**Within US3 (Frontend/Ingress)**: T040-T045 can all be done in parallel (different manifests)

**Within US4 (Helm templates)**: T056-T065 can all be done in parallel (different template files)

### Critical Path

Setup → Foundational → US1 Dockerfiles → US1 Validation → US2 Backend Deploy → US2 Validation → US3 Frontend Deploy → US3 Validation → US4 Helm Creation → US4 Validation → Polish

**Estimated Total Time**: 8-12 hours (with parallelization, experienced developer)

---

## Implementation Strategy

### MVP Scope (Minimum Viable Deployment)

**Phase 1-3 (US1 only)**: Dockerfiles + docker-compose local testing

- Delivers: Containerized services running locally
- Time: ~3-4 hours
- Validation: docker-compose up, verify all services healthy

### Increment 1 (Add US2)

**Phase 4**: Backend/MCP Kubernetes deployment

- Delivers: Backend services running in Minikube
- Time: ~2-3 hours
- Validation: Health endpoints accessible, DB connected

### Increment 2 (Add US3)

**Phase 5**: Frontend + Ingress

- Delivers: Full stack accessible via browser
- Time: ~2-3 hours
- Validation: End-to-end user interaction works

### Increment 3 (Add US4)

**Phase 6-7**: Helm chart + Polish

- Delivers: Production-ready deployment tooling
- Time: ~2-3 hours
- Validation: All success criteria met

---

## Validation Checklist

After completing all tasks:

- [ ] All Functional Requirements (FR-001 through FR-012) satisfied
- [ ] All Success Criteria (SC-001 through SC-005) validated
- [ ] All User Stories have independent tests passing
- [ ] Documentation is complete and accurate
- [ ] No secrets committed to git
- [ ] All images optimized and meet size constraints
- [ ] Deployment scripts work end-to-end
- [ ] Helm chart validates with helm lint
- [ ] Application is fully functional via http://todo.local
- [ ] Operational tooling (kubectl-ai, kagent) documented

---

## Notes

- **Image Builds**: Always run `eval $(minikube docker-env)` before building to avoid needing external registry
- **Secrets**: Never commit k8s/secrets.yaml - only the .template file
- **Ingress**: NGINX addon must be enabled in Minikube before applying Ingress manifest
- **Resource Limits**: Already clarified via /sp.clarify - use exact values in manifests
- **Health Probes**: Use clarified endpoints (/health for Backend/MCP, /\_next/health for Frontend)
- **Testing**: No unit/integration tests requested in spec - focus on smoke tests and deployment validation

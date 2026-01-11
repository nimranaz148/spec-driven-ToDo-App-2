# Feature Specification: Phase 4 Local Kubernetes Deployment

**Feature Branch**: `001-local-kubernetes`
**Created**: 2026-01-11
**Status**: Draft
**Input**: Phase 4 Requirements from "Hackathon II - Todo Spec-Driven Development (1).md"

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Containerize Applications (Priority: P1)

As a DevOps engineer, I want to create optimized Docker images for the Frontend, Backend, and MCP Server using multi-stage builds so that they can be deployed to any container runtime efficiently.

**Why this priority**: Without container images, no deployment is possible. This is the foundational step.

**Independent Test**: Can build all 3 images locally using `docker-compose build` and run them with `docker-compose up`.

**Acceptance Scenarios**:

1. **Given** the source code, **When** running `docker build` for Frontend, **Then** a valid image is created using multi-stage build (Node builder -> Alpine runtime).
2. **Given** the source code, **When** running `docker build` for Backend, **Then** a valid image is created using multi-stage build (Python builder -> Slim runtime).
3. **Given** the source code, **When** running `docker build` for MCP Server, **Then** a valid image is created using multi-stage build.
4. **Given** Docker Desktop with Gordon enabled, **When** analyzing Dockerfiles, **Then** optimizations are suggested and applied.

---

### User Story 2 - Deploy Core Infrastructure & Backend Services (Priority: P2)

As a DevOps engineer, I want to deploy the Backend and MCP Server to a local Minikube cluster with proper namespaces and configuration so that the core logic is operational.

**Why this priority**: Establishes the application backbone and internal communication.

**Independent Test**: Can access Backend `/health` endpoint from within the cluster and Backend can reach MCP Server.

**Acceptance Scenarios**:

1. **Given** Minikube is running, **When** applying namespace manifests, **Then** `todo-app` namespace is created.
2. **Given** secrets and config, **When** applying ConfigMap/Secret manifests, **Then** they exist in `todo-app` namespace.
3. **Given** Backend and MCP images, **When** applying Deployments/Services, **Then** pods are running and Backend can request MCP Server on `http://mcp-server:8001`.
4. **Given** running pods, **When** checking logs, **Then** no connection errors to Database (Neon) are seen.

---

### User Story 3 - Enable Frontend Access (Priority: P3)

As a user, I want to access the Todo Chatbot web interface via a local URL so that I can manage my tasks.

**Why this priority**: Provides the user interface, completing the full stack availability.

**Independent Test**: Can open `http://todo.local` in a browser and interact with the app.

**Acceptance Scenarios**:

1. **Given** Frontend image, **When** applying Deployment, **Then** 2 replicas start successfully.
2. **Given** running Frontend service, **When** configuring Ingress with host `todo.local`, **Then** the application is accessible on port 80.
3. **Given** the web UI, **When** chatting, **Then** requests route through Frontend -> Backend -> MCP -> DB successfully.

---

### User Story 4 - Operational Optimization (Priority: P4)

As a DevOps engineer, I want to package the app with Helm and use AI tools for operations so that deployment is repeatable and manageable.

**Why this priority**: Enhances maintainability and prepares for production (Phase 5).

**Independent Test**: Can deploy the entire stack using `helm install` and query status with `kubectl-ai`.

**Acceptance Scenarios**:

1. **Given** K8s manifests, **When** converting to Helm, **Then** a valid `todo-app` chart is created.
2. **Given** a failed pod, **When** asking `kubectl-ai` "why is it failing?", **Then** it provides root cause analysis.
3. **Given** the cluster, **When** running `kagent`, **Then** it reports cluster health status.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST provide Dockerfiles for Frontend, Backend, and MCP Server using multi-stage builds.
- **FR-002**: backend and mcp-server MUST run as non-root users inside containers.
- **FR-003**: System MUST deploy all components to `todo-app` Kubernetes namespace.
- **FR-004**: Sensitive configuration (DB URL, API Keys) MUST be stored in Kubernetes Secrets.
- **FR-005**: Backend MUST be deployed as a ClusterIP service with 2 replicas.
- **FR-006**: MCP Server MUST be deployed as a ClusterIP service with 1 replica.
- **FR-007**: Frontend MUST be deployed with 2 replicas and exposed via Ingress on `todo.local`.
- **FR-008**: All pods MUST have defined resource requests and limits: Frontend (256Mi memory/0.5 CPU), Backend (512Mi memory/1 CPU), MCP Server (256Mi memory/0.5 CPU).
- **FR-009**: All pods MUST have liveness and readiness probes configured using HTTP GET: Backend/MCP on `/health`, Frontend on `/_next/health`.
- **FR-10**: System MUST include a Helm chart that fully replicates the manifest deployment.
- **FR-11**: System MUST support deployment verification via `kubectl-ai` natural language queries.
- **FR-12**: Backend deployment MUST run Alembic migrations via init container before main application starts.

### Key Entities

- **Container Image**: Docker image artifact for a specific service.
- **Pod**: Running instance of a service (Frontend/Backend/MCP).
- **Service**: Network abstraction for accessing Pods.
- **Ingress**: External access rule for the cluster.
- **Helm Chart**: Package definition for the application stack.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: Deployment of full stack to Minikube takes under 5 minutes.
- **SC-002**: All 3 services (Frontend, Backend, MCP) show "Running" state with 0 restarts after 5 minutes of upregulation.
- **SC-003**: Docker images are optimized: Frontend < 200MB, Backend < 500MB (uncompressed).
- **SC-004**: Application responds to HTTP requests on `todo.local` with 200 OK.
- **SC-005**: Helm lint returns 0 errors.

## Assumptions

- Users have Docker Desktop, Minikube, and Helm installed.
- Neon DB is accessible from the host machine (internet).
- `kubectl-ai` and `kagent` are installed or optional helpers.
- Docker images will be built directly in Minikube's Docker daemon using `eval $(minikube docker-env)` (no external registry required).
- NGINX Ingress Controller will be enabled via `minikube addons enable ingress`.

## Clarifications

### Session 2026-01-12

- Q: Where will Docker images be stored and how will Minikube access them? → A: Use Minikube's built-in Docker daemon (direct access)
- Q: What specific resource requests and limits should be defined for pods? → A: Conservative (Frontend: 256Mi/0.5 CPU, Backend: 512Mi/1 CPU, MCP: 256Mi/0.5 CPU)
- Q: Which endpoints should be used for liveness and readiness probes? → A: Backend/MCP: `/health` for both, Frontend: `/_next/health`
- Q: Which Ingress controller should be used in Minikube? → A: NGINX Ingress Controller (minikube addon)
- Q: Should database schema initialization run automatically or manually? → A: Run migrations via init container

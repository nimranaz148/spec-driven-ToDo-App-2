# Research & Architecture Decisions: Phase 4 Local Kubernetes Deployment

**Status**: Complete (Updated with clarifications)
**Date**: 2026-01-12 (Originally 2026-01-11)

## Clarified Decisions from /sp.clarify

### CD-01: Container Registry Strategy (UPDATED)

**Decision**: Build images directly in Minikube's Docker daemon using `eval $(minikube docker-env)`

**Rationale**:

- Eliminates need for external container registry (Docker Hub, GHCR)
- Faster iteration during development (no push/pull latency)
- Reduces complexity and external dependencies
- Standard practice for local Minikube development
- Images stay local, no accidental public exposure

**Supersedes**: AD-04 below (Docker Hub/GHCR strategy deferred to Phase 5)

---

### CD-02: Resource Limits Specification

**Decision**: Conservative resource allocation for local development

| Service  | Memory Limit | CPU Limit | Replicas |
| -------- | ------------ | --------- | -------- |
| Frontend | 256Mi        | 0.5       | 2        |
| Backend  | 512Mi        | 1.0       | 2        |
| MCP      | 256Mi        | 0.5       | 1        |

**Rationale**:

- Total footprint: ~1.5GB memory, ~3 CPU cores
- Fits comfortably within Minikube's typical 4GB allocation
- Leaves ~2.5GB for Kubernetes system pods, DNS, Ingress controller
- Prevents OOM kills while allowing smooth operation

---

### CD-03: Health Probe Endpoints

**Decision**: Use standardized HTTP GET health probes

| Service  | Endpoint        | Port |
| -------- | --------------- | ---- |
| Backend  | `/health`       | 8000 |
| MCP      | `/health`       | 8001 |
| Frontend | `/_next/health` | 3000 |

**Rationale**:

- Standard conventions (`/health` for APIs, `/_next/health` for Next.js)
- HTTP GET more informative than TCP socket checks
- Same endpoint for liveness and readiness simplifies initial implementation
- Kubernetes can automatically detect and restart failing pods

---

### CD-04: Ingress Controller Selection

**Decision**: NGINX Ingress Controller via Minikube addon

**Rationale**:

- Most widely adopted Kubernetes Ingress controller
- Built into Minikube: `minikube addons enable ingress`
- Zero external dependencies or complex setup
- Extensive documentation and community support
- Supports host-based routing to `todo.local`

---

### CD-05: Database Migration Strategy

**Decision**: Run Alembic migrations via Kubernetes init container

**Rationale**:

- Ensures database schema is current before Backend pods start
- Prevents race conditions (app starting before schema ready)
- Standard Kubernetes pattern for initialization tasks
- Automatic on every deployment (no manual steps)
- Init containers run to completion before main container starts

**Implementation**: Backend Deployment will include initContainer that runs `alembic upgrade head`

---

## Original Architecture Decisions

### AD-02: Helm vs Raw Kubernetes Manifests

**Decision**: Use both - Raw manifests for Minikube, Helm for production (Phase 5)

**Rationale**:

- Raw manifests simpler for local development
- Helm provides better value for multi-environment production
- Progressive approach: Learn K8s first, then use Helm
- Helm enables easier upgrades in production

**Trade-offs**:

- Pros: Maintains two approaches for different use cases
- Cons: Slightly more maintenance overhead

**Alternatives Considered**:

1. Helm only - Rejected (overhead for local dev)
2. K8s manifests only - Rejected (no production best practices)

---

### AD-03: NodePort vs LoadBalancer (Frontend Service)

**Decision**: NodePort for Minikube, LoadBalancer for production (Phase 5)

**Rationale**:

- Minikube doesn't fully support LoadBalancer
- NodePort works reliably in Minikube with port forwarding
- LoadBalancer is production-ready for cloud providers
- Ingress handles external access either way

**Trade-offs**:

- Pros: Works in both environments with appropriate type
- Cons: Different service types require configuration awareness

**Alternatives Considered**:

1. LoadBalancer only - Rejected (Minikube limitation)
2. ClusterIP + Ingress only - Rejected (port forwarding needed for dev)

---

### AD-04: Docker Registry Strategy

**Decision**: Use Docker Hub for development, GHCR for production

**Rationale**:

- Docker Hub free tier sufficient for development images
- GHCR integrated with GitHub Actions (CI/CD ready)
- GitHub token auth more secure than Docker Hub password
- Separate registries prevent mixing dev/prod images

**Trade-offs**:

- Pros: Free for both, GHCR better CI/CD integration
- Cons: Two registries to manage

**Alternatives Considered**:

1. Docker Hub only - Rejected (CI/CD integration harder)
2. GHCR only - Rejected (Docker Hub more familiar for dev)

## Technical Stacks Confirmed

| Component           | Choice              | Reason                                        |
| ------------------- | ------------------- | --------------------------------------------- |
| Frontend Base Image | node:20-alpine      | Small size, secure, standard for Next.js      |
| Backend Base Image  | python:3.13-slim    | Small size, compatible with UV/Python 3.13    |
| K8s Local           | Minikube            | Standard local K8s, supports addons (ingress) |
| AIOps               | kubectl-ai + Gordon | AI-assisted debugging and optimization        |

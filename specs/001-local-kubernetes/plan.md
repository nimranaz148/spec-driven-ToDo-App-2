# Implementation Plan: Local Kubernetes Deployment

**Branch**: `001-local-kubernetes` | **Date**: 2026-01-12 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-local-kubernetes/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Deploy the existing Todo Chatbot application (Frontend, Backend, MCP Server) to a local Minikube Kubernetes cluster using containerized services. Implementation uses multi-stage Docker builds for optimized images, raw Kubernetes manifests for deployment with a Helm chart wrapper for operational repeatability. All components run in the `todo-app` namespace with proper resource limits, health probes, and automated database migrations via init containers.

## Technical Context

**Language/Version**: Python 3.11 (Backend/MCP), Node.js 20/Next.js 15 (Frontend)  
**Primary Dependencies**: FastAPI (Backend), better-auth (Frontend), MCP SDK (MCP Server), Docker 24+, Minikube 1.32+, Helm 3.14+  
**Storage**: Neon PostgreSQL (external, already deployed), Docker volumes for transient data  
**Testing**: pytest (Backend), Jest/Playwright (Frontend), docker-compose smoke tests  
**Target Platform**: Minikube on Docker Desktop (Windows/Mac/Linux), Kubernetes 1.28+  
**Project Type**: Web application (Frontend + Backend + MCP microservice)  
**Performance Goals**: <5 minute full stack deployment, <3 second cold start per pod  
**Constraints**: <200MB Frontend image, <500MB Backend image, fit within 4GB Minikube default  
**Scale/Scope**: Local development deployment, 5 total pods (2 Frontend + 2 Backend + 1 MCP)

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**Status**: PASS (Constitution template is placeholder - no specific gates defined yet)

This deployment phase adds infrastructure tooling (Dockerfiles, K8s manifests, Helm charts) to existing validated application code. No new libraries or architectural changes to the core application. Infrastructure artifacts follow standard patterns (multi-stage builds, resource limits, probes).

## Project Structure

### Documentation (this feature)

```text
specs/001-local-kubernetes/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── helm-values-schema.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure (Frontend + Backend + MCP Server)
backend/
├── src/
│   ├── models/          # SQLAlchemy models (existing)
│   ├── services/        # Business logic (existing)
│   ├── routes/          # FastAPI endpoints (existing)
│   └── main.py          # FastAPI app (existing)
├── tests/               # Existing test suite
├── Dockerfile           # NEW: Multi-stage Python build
└── alembic/             # Existing DB migrations

frontend/
├── src/
│   ├── components/      # React components (existing)
│   ├── app/             # Next.js pages (existing)
│   └── lib/             # Utilities (existing)
├── tests/               # Existing test suite
└── Dockerfile           # NEW: Multi-stage Node build

backend/src/mcp_server.py    # Existing MCP server (currently in backend)
mcp/                         # NEW: Separate MCP deployment artifacts
└── Dockerfile               # NEW: Multi-stage Python build (uses backend code)

k8s/                         # NEW: Kubernetes manifests
├── namespace.yaml
├── configmap.yaml
├── secrets.yaml           # Template (not in git)
├── backend-deployment.yaml
├── backend-service.yaml
├── mcp-deployment.yaml
├── mcp-service.yaml
├── frontend-deployment.yaml
├── frontend-service.yaml
└── ingress.yaml

helm/                        # NEW: Helm chart
└── todo-app/
    ├── Chart.yaml
    ├── values.yaml
    ├── values-dev.yaml
    └── templates/           # Mirrors k8s/ structure
```

**Structure Decision**: Using the existing web application structure (frontend/ and backend/ directories) with new deployment artifacts in k8s/ and helm/ directories. MCP Server remains colocated with backend code but gets its own Dockerfile and Kubernetes deployment for independent scaling.

## Complexity Tracking

N/A - No constitution violations. Infrastructure tooling is additive and follows standard patterns.

---

## Phase 0: Research & Architecture Decisions

**Status**: ✅ Complete

**Output**: [research.md](research.md)

**Key Decisions Documented**:

1. Container registry strategy (Minikube Docker daemon)
2. Resource allocation (conservative limits for local dev)
3. Health probe configuration (HTTP GET on standard endpoints)
4. Ingress controller selection (NGINX via addon)
5. Database migration strategy (init containers)
6. Multi-stage Docker builds (size optimization)
7. Service architecture (ClusterIP + Ingress)
8. Namespace isolation
9. Secret management
10. Helm chart approach

All "NEEDS CLARIFICATION" items from Technical Context resolved through /sp.clarify session.

---

## Phase 1: Design & Contracts

**Status**: ✅ Complete

### Artifacts Generated

1. **[data-model.md](data-model.md)** - Kubernetes resource definitions

   - Namespace, ConfigMap, Secret entities
   - Deployment specs for Frontend, Backend, MCP with init containers
   - Service definitions (ClusterIP for internal, Ingress for external)
   - Resource relationships and validation rules

2. **[contracts/helm-values-schema.yaml](contracts/helm-values-schema.yaml)** - Helm chart configuration contract

   - Defines all configurable values (replicas, resources, images, ingress)
   - Validation schema for user-provided values
   - Defaults aligned with clarified resource limits

3. **[quickstart.md](quickstart.md)** - Deployment procedures
   - Prerequisites (Docker Desktop, Minikube, Helm, kubectl)
   - Step-by-step: Minikube startup, image builds, manifest apply, verification
   - Commands for building in Minikube daemon: `eval $(minikube docker-env)`
   - Helm deployment alternative: `helm install todo-app ./helm/todo-app`
   - Troubleshooting guide

### Agent Context Update

Will be executed after Phase 2 (tasks generation) as part of `/sp.tasks` workflow.

---

## Phase 2: Implementation Strategy

### Dockerfile Creation

**Location**: Backend, Frontend, MCP directories

**Backend Dockerfile** (`backend/Dockerfile`):

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Stage 2: Runtime
FROM python:3.11-slim
RUN useradd -m -u 1000 appuser
WORKDIR /app
COPY --from=builder /app ./
USER appuser
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile** (`frontend/Dockerfile`):

```dockerfile
# Stage 1: Dependencies
FROM node:20 AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Builder
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Runtime
FROM node:20-alpine
RUN adduser -D -u 1000 appuser
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.* ./
COPY --from=builder /app/package.json ./
USER appuser
EXPOSE 3000
CMD ["npm", "start"]
```

**MCP Dockerfile** (`mcp/Dockerfile` or `backend/Dockerfile.mcp`):

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY backend/pyproject.toml ./
RUN pip install --no-cache-dir -e .
COPY backend/src/ ./src/

# Stage 2: Runtime
FROM python:3.11-slim
RUN useradd -m -u 1000 appuser
WORKDIR /app
COPY --from=builder /app ./
USER appuser
EXPOSE 8001
CMD ["python", "-m", "src.mcp_server"]
```

---

### Kubernetes Manifests

**Location**: `k8s/` directory

**Manifest List**:

1. `namespace.yaml` - Todo-app namespace
2. `configmap.yaml` - Non-sensitive config (service URLs, log levels)
3. `secrets.yaml.template` - Secret template (user fills actual values)
4. `backend-deployment.yaml` - Backend with init container for migrations
5. `backend-service.yaml` - ClusterIP service on port 8000
6. `mcp-deployment.yaml` - MCP Server pods
7. `mcp-service.yaml` - ClusterIP service on port 8001
8. `frontend-deployment.yaml` - Frontend pods
9. `frontend-service.yaml` - ClusterIP service on port 3000
10. `ingress.yaml` - NGINX Ingress for todo.local

**Key Manifest Features**:

- `imagePullPolicy: Never` (local Minikube images)
- Resource requests/limits per CD-02 (256Mi/0.5 for Frontend/MCP, 512Mi/1 for Backend)
- Health probes per CD-03 (/health for Backend/MCP, /\_next/health for Frontend)
- Init container in backend-deployment runs `alembic upgrade head`
- Labels: `app: todo-chatbot`, `component: <service-name>`

---

### Helm Chart

**Location**: `helm/todo-app/`

**Chart Structure**:

```
helm/todo-app/
├── Chart.yaml              # Chart metadata (version, description)
├── values.yaml             # Default values
├── values-dev.yaml         # Dev environment overrides
├── values-prod.yaml        # Prod environment overrides (future)
└── templates/
    ├── _helpers.tpl        # Template helpers
    ├── namespace.yaml
    ├── configmap.yaml
    ├── secrets.yaml
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── mcp-deployment.yaml
    ├── mcp-service.yaml
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml
    └── ingress.yaml
```

**values.yaml Parameterization**:

```yaml
environment: local

images:
  frontend:
    repository: frontend
    tag: latest
    pullPolicy: Never
  backend:
    repository: backend
    tag: latest
    pullPolicy: Never
  mcp:
    repository: mcp
    tag: latest
    pullPolicy: Never

replicas:
  frontend: 2
  backend: 2
  mcp: 1

resources:
  frontend:
    limits:
      memory: 256Mi
      cpu: "0.5"
    requests:
      memory: 256Mi
      cpu: "0.5"
  backend:
    limits:
      memory: 512Mi
      cpu: "1"
    requests:
      memory: 512Mi
      cpu: "1"
  mcp:
    limits:
      memory: 256Mi
      cpu: "0.5"
    requests:
      memory: 256Mi
      cpu: "0.5"

ingress:
  enabled: true
  host: todo.local
  ingressClassName: nginx

config:
  logLevel: info
  nodeEnv: production

secrets:
  databaseUrl: "" # User must provide
  betterAuthSecret: ""
  betterAuthUrl: "http://todo.local"
  openaiApiKey: ""
```

---

### Deployment Workflow

**Manual Deployment** (k8s manifests):

```bash
# 1. Start Minikube with Ingress addon
minikube start --driver=docker
minikube addons enable ingress

# 2. Point Docker to Minikube daemon
eval $(minikube docker-env)

# 3. Build images
docker build -t frontend:latest ./frontend
docker build -t backend:latest ./backend
docker build -t mcp:latest -f mcp/Dockerfile .

# 4. Create namespace
kubectl apply -f k8s/namespace.yaml

# 5. Create secrets (copy template, fill values)
cp k8s/secrets.yaml.template k8s/secrets.yaml
# Edit secrets.yaml with actual values
kubectl apply -f k8s/secrets.yaml

# 6. Apply remaining manifests
kubectl apply -f k8s/

# 7. Add /etc/hosts entry
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts

# 8. Wait for pods
kubectl wait --for=condition=ready pod -l app=todo-chatbot -n todo-app --timeout=300s

# 9. Access application
open http://todo.local
```

**Helm Deployment**:

```bash
# 1-3: Same Minikube and image build steps

# 4. Install with Helm (creates namespace automatically)
helm install todo-app ./helm/todo-app \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY"

# 5-9: Same verification steps
```

---

### Testing & Validation

**Smoke Tests**:

1. All pods Running: `kubectl get pods -n todo-app` (0 restarts expected)
2. Health checks pass:
   ```bash
   kubectl port-forward -n todo-app svc/backend-service 8000:8000
   curl http://localhost:8000/health  # Should return 200
   ```
3. Ingress accessible: `curl http://todo.local` (Should return HTML)
4. Database connectivity: Check backend logs for successful migrations
5. End-to-end: Login via UI, create task, verify in database

**Performance Validation** (SC-001, SC-002, SC-003):

- Deployment time: `time helm install ...` (< 5 minutes)
- Image sizes: `docker images | grep -E '(frontend|backend|mcp)'` (Frontend <200MB, Backend <500MB)
- Pod stability: Check after 5 minutes for restarts

**Helm Validation** (SC-005):

```bash
helm lint ./helm/todo-app  # Must return 0 errors
```

---

### Operational Tooling

**kubectl-ai Integration** (FR-11):

```bash
# Install kubectl-ai (optional helper)
# https://github.com/sozercan/kubectl-ai

# Example queries
kubectl ai "why is the backend pod failing?"
kubectl ai "show me resource usage for frontend pods"
kubectl ai "how do I scale backend to 3 replicas?"
```

**kagent Integration** (US4):

```bash
# Install kagent (optional helper)
# AI-assisted cluster health monitoring

kagent health  # Reports cluster and app status
```

**Gordon (Docker Desktop)** (US1):

- Enable Gordon in Docker Desktop settings
- Analyze Dockerfiles for optimization suggestions
- Apply recommendations to meet SC-003 image size constraints

---

## Next Steps

**After /sp.plan completion**:

1. Run `/sp.tasks` to break down implementation into atomic tasks
2. Tasks will cover:
   - Dockerfile creation (US1)
   - K8s manifest authoring (US2)
   - Helm chart creation (US4)
   - Testing and validation
   - Documentation updates

**Phase 5 Preparation** (Future):

- Migrate registry to GHCR (update AD-04 decision)
- Change Service types from ClusterIP to LoadBalancer
- Add production Helm values with tighter security
- Implement horizontal pod autoscaling (HPA)

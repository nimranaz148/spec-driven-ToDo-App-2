# Phase 4: Kubernetes Deployment - Project Constitution

**Project**: Evolution of Todo
**Phase**: Phase 4 - Local Kubernetes Deployment
**Version**: 1.0.0
**Ratified**: December 24, 2025
**Status**: Active

---

## CLAUDE.md Integration (READ FIRST)

This constitution MUST be read by all agents in this context:
1. **Root CLAUDE.md** - Project-wide rules and phase-specific agent/skill mapping
2. **Backend CLAUDE.md** - Backend-specific patterns and configurations
3. **Frontend CLAUDE.md** - Frontend-specific patterns and configurations
4. **This Constitution** - Phase 4 specific principles and constraints

Agents MUST reference the appropriate CLAUDE.md file based on their scope.

---

## Project Overview

Phase 4 transforms the Phase 3 Todo Chatbot into a containerized application deployable on:
- **Minikube** - Local Kubernetes cluster for development and testing
- **DigitalOcean DOKS** (Phase 5) - Production Kubernetes deployment

This phase introduces:
- Docker containerization (Dockerfiles, Docker Compose)
- Kubernetes manifests (Deployments, Services, Ingress)
- Helm charts (Package management)
- AIOps tools (kubectl-ai, Kagent, Docker AI/Gordon)

---

## Core Principles

### Principle I: Infrastructure as Code (NON-NEGOTIABLE)

**Description**: All infrastructure must be defined as code, not manually configured in UI/console.

**Rules**:
- All Kubernetes manifests must be version-controlled in `k8s/` directory
- All Helm charts must be version-controlled in `helm/` directory
- All Dockerfiles must be version-controlled
- No manual `kubectl` edits in production - always apply from files

**Rationale**:
- Ensures reproducibility across environments
- Enables audit trail of infrastructure changes
- Facilitates rollback and disaster recovery

### Principle II: Multi-Stage Builds (NON-NEGOTIABLE)

**Description**: Docker images must use multi-stage builds to minimize final image size.

**Rules**:
- Frontend: Builder stage with full Node.js, Runtime stage with Alpine
- Backend: Builder stage with build tools, Runtime stage with only runtime deps
- MCP Server: Minimal base image, 100m-300m CPU, 64-128Mi memory

**Rationale**:
- Reduces attack surface
- Faster deployment (smaller images)
- Lower storage costs

### Principle III: Resource Limits (NON-NEGOTIABLE)

**Description**: All containers must have defined resource requests and limits.

**Rules**:
- Every Deployment must specify `resources.requests` and `resources.limits`
- Use CPU in millicores (m) and memory in Mi
- Frontend: 100m-500m CPU, 128-256Mi memory
- Backend: 200m-1000m CPU, 256-512Mi memory
- MCP Server: 100m-300m CPU, 64-128Mi memory

**Rationale**:
- Prevents resource starvation across pods
- Enables Kubernetes scheduler optimization
- Prevents runaway resource consumption

### Principle IV: Health Probes (NON-NEGOTIABLE)

**Description**: All containers must have liveness and readiness probes.

**Rules**:
- Frontend: HTTP GET `/` on port 3000
- Backend: HTTP GET `/health` on port 8000
- MCP Server: HTTP GET `/health` on port 8001
- Initial delay: Frontend 30s, Backend 30s, MCP 10s
- Period: 10s for liveness, 5s for readiness

**Rationale**:
- Enables Kubernetes to restart failed containers automatically
- Routes traffic only to ready pods
- Improves overall application availability

### Principle V: Service Discovery (NON-NEGOTIABLE)

**Description**: Services must communicate using Kubernetes DNS, not localhost.

**Rules**:
- Frontend → Backend: `http://backend:8000` (not localhost)
- Backend → MCP Server: `http://mcp-server:8001` (not localhost)
- External Access: Only via Ingress (frontend exposed, others internal)
- Services use ClusterIP type except frontend (NodePort for Minikube)

**Rationale**:
- Enables service-to-service communication within cluster
- Supports horizontal scaling of individual services
- Maintains separation of concerns

### Principle VI: Secrets Management (NON-NEGOTIABLE)

**Description**: Sensitive data must never be hardcoded or committed to Git.

**Rules**:
- All secrets in Kubernetes `Secret` resources
- No API keys, passwords, or tokens in manifests or Helm values
- Use environment variable references: `valueFrom.secretKeyRef`
- `.env` files must be in `.gitignore`
- Helm values for secrets use empty defaults, set via `--set` or separate files

**Rationale**:
- Prevents credential leakage in version control
- Enables different secrets per environment
- Supports rotation without code changes

### Principle VII: Immutable Infrastructure (NON-NEGOTIABLE)

**Description**: Apply changes via new manifests/charts, no in-place modifications.

**Rules**:
- Use Helm `upgrade` for changes, not `kubectl edit`
- Apply new manifests for updates, never patch existing resources
- State changes go through deployment rollouts, not manual pod edits

**Rationale**:
- Ensures infrastructure is reproducible from code
- Enables rollback to known good states
- Prevents configuration drift

### Principle VIII: AIOps Integration (ENCOURAGED)

**Description**: Use AI-powered tools for operations when available.

**Rules**:
- Use `docker ai` (Gordon) for Docker optimization and debugging
- Use `kubectl-ai` for Kubernetes operations and troubleshooting
- Use `kagent` for cluster health analysis
- AI suggestions are advisory - human approval required for production

**Rationale**:
- Reduces operations learning curve
- Provides intelligent error analysis
- Enables faster incident response

---

## Technology Stack

### Containerization

| Component | Base Image | Runtime | Port |
|-----------|-------------|----------|-------|
| Frontend | node:20-alpine | Node.js | 3000 |
| Backend | python:3.13-slim | Python 3.13 | 8000 |
| MCP Server | python:3.13-slim | Python 3.13 | 8001 |

### Local Kubernetes

| Tool | Version | Purpose |
|------|---------|---------|
| Minikube | Latest | Local cluster |
| kubectl | Latest | Cluster management |
| Docker | Latest | Container runtime |

### AIOps Tools

| Tool | Purpose | Installation |
|------|---------|-------------|
| Docker AI (Gordon) | Docker operations | Docker Desktop 4.53+ (beta feature) |
| kubectl-ai | K8s operations via AI | `go install github.com/GoogleCloudPlatform/kubectl-ai` |
| Kagent | Cluster monitoring/analysis | `go install github.com/kagent-dev/kagent` |

### Package Management

| Tool | Purpose |
|------|---------|
| Helm | Package and template K8s manifests |
| Helm Charts | todo-app (1.0.0) |

### Container Registry

| Environment | Registry | Notes |
|-----------|----------|----------|
| Local | Docker (local) | For Minikube testing |
| Development | Docker Hub | Free public tier |
| Production (Phase 5) | GHCR or Docker Hub | Private registry preferred |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   MINIKUBE KUBERNETES CLUSTER                     │
│                                                                     │
│  ┌─────────────────────┐  ┌─────────────────────┐               │
│  │   FRONTEND POD      │  │   BACKEND POD       │               │
│  │  (Next.js 16+)     │  │  (FastAPI + AI)     │               │
│  │  Replicas: 2       │  │  Replicas: 2         │               │
│  │  Port: 3000         │  │  Port: 8000         │               │
│  │  CPU: 100-500m     │  │  CPU: 200-1000m    │               │
│  │  RAM: 128-256Mi     │  │  RAM: 256-512Mi     │               │
│  └──────────┬──────────┘  └──────────┬──────────┘               │
│             │                          │                               │
│             │                          │                               │
│  ┌──────────▼──────────────────────────▼───────────────────────────┐   │
│  │                NEON POSTGRESQL (EXTERNAL)                  │   │
│  │         Serverless - cloud.neon.tech                       │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│             │                          │                               │
│             ▼                          ▼                               │
│  ┌─────────────────────┐  ┌─────────────────────┐               │
│  │  MCP SERVER POD     │  │   INGRESS (NGINX)  │               │
│  │  (FastMCP)         │  │  todo.local          │               │
│  │  Replicas: 1       │  │  Routes: / → Frontend              │
│  │  Port: 8001         │  └─────────────────────┘               │
│  │  CPU: 100-300m     │                                         │
│  │  RAM: 64-128Mi      │                                         │
│  └─────────────────────┘                                         │
│                                                                     │
│  Service Discovery:                                                   │
│  - Frontend → Backend: http://backend:8000                      │
│  - Backend → MCP: http://mcp-server:8001                        │
│  - User → App: http://todo.local (via Ingress)                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────────────┘

AIOps Layer:
┌───────────────────────────────────────────────────────────────────────────┐
│  Docker AI (Gordon) │  kubectl-ai │  Kagent              │
│  Docker optimization │  K8s operations  │  Cluster monitoring  │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## Claude Code Integration

### Phase 4 Agents

| Agent | When to Use | Coupled Skills |
|-------|--------------|-----------------|
| **@devops-kubernetes-builder** | Kubernetes manifests, Minikube setup | kubernetes-deployment, minikube-setup |
| **@docker-containerization-builder** | Dockerfiles, Docker Compose | docker-setup |
| **@aiops-helm-builder** | Helm charts, package management | helm-charts-setup, aiops-gordon |

### Phase 4 Skills

| Skill | Purpose | Directory |
|-------|---------|-----------|
| `docker-setup` | Dockerfile creation, Docker Compose | `.claude/skills/docker-setup/` |
| `kubernetes-deployment` | K8s manifests, Minikube operations | `.claude/skills/kubernetes-deployment/` |
| `helm-charts-setup` | Helm chart creation and values | `.claude/skills/helm-charts-setup/` |
| `aiops-gordon` | Docker AI (Gordon) usage | `.claude/skills/aiops-gordon/` |
| `minikube-setup` | Minikube installation and operations | `.claude/skills/minikube-setup/` |

### CLAUDE.md Hierarchy

```
/root/CLAUDE.md                    # Root - maps agents/skills to all phases
  │
  ├─> prompts/constitution-prompt-phase-4.md  # THIS FILE
  │
  ├─> backend/CLAUDE.md           # Backend patterns (for reference)
  │
  ├─> frontend/CLAUDE.md          # Frontend patterns (for reference)
  │
  ├─> .claude/agents/
  │   ├─> devops-kubernetes-builder.md      # K8s agent
  │   ├─> docker-containerization-builder.md  # Docker agent
  │   └─> aiops-helm-builder.md           # Helm agent
  │
  └─> .claude/skills/
      ├─> docker-setup/SKILL.md
      ├─> kubernetes-deployment/SKILL.md
      ├─> helm-charts-setup/SKILL.md
      ├─> aiops-gordon/SKILL.md
      └─> minikube-setup/SKILL.md
```

---

## Development Workflow

### Phase 4 Development Cycle

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE 4 DEVELOPMENT CYCLE                      │
│                                                                 │
│  1. DOCKERIZE                                           │
│     ├─> @docker-containerization-builder                         │
│     ├─> Create Dockerfiles (frontend, backend, mcp)           │
│     ├─> Create docker-compose.yml                             │
│     └─> Build and test images locally                          │
│                                                                 │
│  2. CREATE K8S MANIFESTS                                  │
│     ├─> @devops-kubernetes-builder                             │
│     ├─> Create namespace, configmap, secret                       │
│     ├─> Create deployments (3 services)                          │
│     ├─> Create services (internal + external)                     │
│     └─> Create ingress for external access                        │
│                                                                 │
│  3. HELM CHART CREATION (Optional but Recommended)          │
│     ├─> @aiops-helm-builder                                  │
│     ├─> Convert manifests to Helm templates                                 │
│                                                                 │
│  4. PREPARE FOR PHASE 5                                   │
│     ├─> Add Dapr annotations (for Phase 5)                    │
│     ├─> Prepare Kafka integration (for Phase 5)                  │
│     └─> Update Helm values for production                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

### Container Specifications

| Service | Image Name | Port | Health Check | Replicas |
|----------|-------------|-------|---------------|----------|
| Frontend | todo-frontend:latest | 3000 | GET / | 2 |
| Backend | todo-backend:latest | 8000 | GET /health | 2 |
| MCP Server | todo-mcp-server:latest | 8001 | GET /health | 1 |

### Service Configuration

| Service Name | Type | Port | Selector |
|-------------|-------|-------|-----------|
| frontend-service | NodePort (local) / LoadBalancer (cloud) | 80:3000 | app: frontend |
| backend-service | ClusterIP | 8000 | app: backend |
| mcp-service | ClusterIP | 8001 | app: mcp-server |

### Environment Variables

#### Frontend
```env
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
NEXT_PUBLIC_API_URL=http://backend:8000
NEXT_PUBLIC_MCP_URL=http://mcp-server:8001
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=<from .env>
```
**Note**: Copy from `frontend/.env` when deploying.

#### Backend
```env
DATABASE_URL=<from .env>
GEMINI_API_KEY=<from .env>
BETTER_AUTH_SECRET=<from .env>
MCP_SERVER_URL=http://mcp-server:8001
```
**Note**: Copy from `backend/.env` when deploying.

#### MCP Server
```env
GEMINI_API_KEY=<from .env>
```
**Note**: Copy from `backend/.env` when deploying.

---

## Environment Variable Reference for Deployment

All required environment variables should be in your local `.env` files. When deploying to Kubernetes, you will reference these values in ConfigMap and Secret resources.

### Required Variables

| Variable | Service | Source | Purpose |
|-----------|----------|---------|----------|
| `DATABASE_URL` | Backend | Neon PostgreSQL connection string |
| `GEMINI_API_KEY` | Backend, MCP Server | Google Gemini API key |
| `BETTER_AUTH_SECRET` | Backend | Better Auth JWT secret |
| `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` | Frontend | OpenAI ChatKit domain key |
| `MCP_SERVER_URL` | Backend | MCP server URL (internal K8s) |

### Deployment Commands

When using `/sp.implement` or manual deployment, reference your `.env` file:

```bash
# Backend - load from .env
source backend/.env

# Frontend - load from .env
source frontend/.env
```

---

## Natural Language Commands for kubectl-ai

The following commands can be used with `kubectl-ai`:

| Request | Expected Action |
|---------|----------------|
| "Deploy todo app to Minikube" | Apply manifests, verify pods |
| "Scale backend to 3 replicas" | Update backend deployment replicas |
| "Check why pods are failing" | Analyze pod logs and events |
| "Get resource usage across namespace" | Show CPU/memory metrics |
| "Optimize resource allocation" | Suggest adjustments |
| "Rollback to previous deployment" | Execute helm rollback |

---

## Code Quality Standards

### Dockerfile Standards

```dockerfile
# Multi-stage build required
FROM <base>:<version> AS builder

# Install build dependencies
RUN <install commands>

# Copy source
COPY . .

# Build application
RUN <build commands>

# Runtime stage (minimal)
FROM <base-minimal>:<version>

# Copy only runtime artifacts
COPY --from=builder <artifacts> <destination>

# Non-root user
RUN useradd -m -u 1000 appuser
USER appuser

EXPOSE <port>
HEALTHCHECK <check-command>
CMD <entrypoint>
```

### Kubernetes Manifest Standards

```yaml
# All manifests require:
apiVersion: <correct-version>  # Check API versions
kind: <resource-kind>
metadata:
  name: <kebab-case-name>
  namespace: todo-app
  labels:  # Labels for selector matching
    app: <app-name>
    tier: <frontend|backend>
spec:
  replicas: <number>
  selector:  # Must match pod labels
    matchLabels:
      app: <app-name>
  template:
    metadata:
      labels:  # Must match selector
        app: <app-name>
    spec:
      containers:
      - resources:  # Requests AND limits required
          requests:
            cpu: <m>
            memory: <Mi>
          limits:
            cpu: <m>
            memory: <Mi>
        livenessProbe:  # Required
          httpGet:
            path: <endpoint>
            port: <port>
        readinessProbe:  # Required
          httpGet:
            path: <endpoint>
            port: <port>
```

### Helm Template Standards

```yaml
# Use Helm helper functions
{{- define "todo-app.name" }}{{ end }}  # Define helpers
{{- include "todo-app.labels" . | nindent 4 }}  # Include templates
{{- range $key, $value := .Values.env }}  # Iteration

# All values should be configurable via values.yaml
# Use defaults in templates for optional values
{{ .Values.some.value | default "default-value" }}
```

---

## Environment Variables

### Development (Minikube)

| Variable | Value | Source |
|----------|-------|--------|
| MINIKUBE_CPU | 4 | Command line |
| MINIKUBE_MEMORY | 8192 | Command line |
| DATABASE_URL | Neon connection string | Neon console |
| GEMINI_API_KEY | Gemini API key | Secret |
| BETTER_AUTH_SECRET | Auth secret | Secret |

### Production (Phase 5)

| Variable | Value | Source |
|----------|-------|--------|
| REGISTRY | ghcr.io or docker.io | Container registry |
| REPLICAS_FRONTEND | 3+ | Helm values |
| REPLICAS_BACKEND | 3+ | Helm values |
| ENABLE_HPA | true | Helm values |

---

## Security Checklist

- [ ] No API keys or secrets in Dockerfiles
- [ ] No secrets in Kubernetes manifests
- [ ] All secrets in Kubernetes Secret resources
- [ ] All containers run as non-root user
- [ ] Minimal base images (alpine, slim)
- [ ] Resource limits defined for all containers
- [ ] Liveness probes configured
- [ ] Readiness probes configured
- [ ] .env files in .gitignore
- [ ] Image scanning enabled (Docker Scout or Trivy)
- [ ] RBAC configured (for production)
- [ ] Network policies defined (for production)
- [ ] TLS enabled for Ingress (for production)

---

## Testing Strategy

### Unit Tests
- Dockerfiles: `docker build` succeeds
- Manifests: `kubectl apply --dry-run` succeeds
- Helm charts: `helm lint` passes

### Integration Tests (Minikube)
```bash
# 1. Deploy application
kubectl apply -f k8s/ -n todo-app

# 2. Verify all pods are Running
kubectl get pods -n todo-app

# 3. Verify services have endpoints
kubectl get endpoints -n todo-app

# 4. Test connectivity
kubectl run test-pod --rm -it --image=curlimages/curl \
  -- curl http://backend:8000/health

# 5. End-to-end test
minikube service frontend -n todo-app
# Then manually test: create task, chat with AI
```

### AIOps Tests
- `docker ai "What can you do?"` - Verify Gordon works
- `kubectl-ai "analyze cluster"` - Verify kubectl-ai works
- `kagent "check health"` - Verify Kagent works

---

## Phase 4 Deliverables

### Required Files
1. `frontend/Dockerfile` - Multi-stage Next.js container
2. `backend/Dockerfile` - Multi-stage FastAPI container
3. `backend/Dockerfile.mcp` - MCP Server container
4. `docker-compose.yml` - Local orchestration
5. `k8s/` - Kubernetes manifests directory
   - `00-namespace.yaml`
   - `01-configmap.yaml`
   - `02-secret.yaml`
   - `03-mcp-server-deployment.yaml`
   - `04-mcp-server-service.yaml`
   - `05-backend-deployment.yaml`
   - `06-backend-service.yaml`
   - `07-frontend-deployment.yaml`
   - `08-frontend-service.yaml`
   - `09-ingress.yaml`
6. `helm/todo-app/` - Helm chart directory
   - `Chart.yaml`
   - `values.yaml`
   - `values-dev.yaml`
   - `values-staging.yaml`
   - `values-prod.yaml`
   - `templates/` directory with all K8s resources
7. Documentation:
   - README deployment instructions
   - Minikube setup guide
   - Troubleshooting guide

### Working Application
- Application accessible at http://todo.local (via Minikube)
- Frontend can connect to backend
- Backend can connect to MCP server
- All pods healthy (no restart loops)
- Resource usage within limits

---

## Phase 5 Considerations

While implementing Phase 4, prepare for Phase 5:

### Dapr Integration
Add Dapr annotations to deployments (disabled in Phase 4, enabled in Phase 5):
```yaml
annotations:
  dapr.io/enabled: "false"  # Phase 4: false, Phase 5: true
  dapr.io/app-id: "backend"
  dapr.io/app-port: "8000"
  dapr.io/config: "app-config"
```

### Kafka Preparation
Prepare for Kafka topics in Phase 5:
- `task-events` - All task CRUD operations
- `reminders` - Scheduled reminders
- `task-updates` - Real-time sync

### Cloud Registry
Prepare container registry for Phase 5:
- GitHub Container Registry (GHCR) - Free for public projects
- Docker Hub - Free public tier, private requires paid
- DigitalOcean Container Registry - Included with DOKS

### Advanced Dapr Building Blocks (Phase 5)
Prepare for:
- Dapr Pub/Sub (Kafka abstraction)
- Dapr State Management (conversation state)
- Dapr Service Invocation (service-to-service calls)
- Dapr Secrets Management (API keys)
- Dapr Bindings (cron for reminders)

---

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Docker AI (Gordon)](https://docs.docker.com/ai/gordon/)
- [kubectl-ai GitHub](https://github.com/GoogleCloudPlatform/kubectl-ai)
- [Kagent GitHub](https://github.com/kagent-dev/kagent)
- [Dapr Documentation](https://docs.dapr.io/)
- [Hackathon II Spec](./Hackathon\ II\ -\ Todo\ Spec-Driven\ Development.md)

---

**Constitution Version**: 1.0.0
**Last Updated**: December 24, 2025
**Phase**: Phase 4 - Local Kubernetes Deployment

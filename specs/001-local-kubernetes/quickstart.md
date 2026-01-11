# Quickstart: Phase 4 Local Kubernetes Deployment

**Concept**: Local Cloud-Native Development Environment
**Status**: Beta

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [Helm](https://helm.sh/docs/intro/install/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

## 1. Environment Setup

Start Minikube and configure Docker to use the Minikube daemon (avoids pushing images to registry).

```bash
# Start Minikube with Ingress
minikube start --driver=docker --addons=ingress

# Point local Docker CLI to Minikube's Docker daemon (Run in every new terminal)
eval $(minikube docker-env)

# Verify
docker ps  # Should see k8s containers
```

**DNS Setup**:
Add the following line to your `/etc/hosts` (Mac/Linux) or `C:\Windows\System32\drivers\etc\hosts` (Windows, run as Admin):

```
127.0.0.1 todo.local
```
*(or use `$(minikube ip) todo.local` if on Linux/native)*

## 2. Build Container Images

Build images directly into the Minikube registry.

```bash
# Using Makefile (Recommended)
make build-images

# OR Manual
docker build -t backend:latest ./backend
docker build -t mcp:latest -f mcp/Dockerfile .
docker build -t frontend:latest ./frontend
```

## 3. Deploy Application

**Set Environment Variables**:
```bash
export DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require"
export OPENAI_API_KEY="sk-..."
```

### Option A: Helper Script (Recommended)
```bash
./scripts/deploy-backend.sh
```

### Option B: Helm (Production-like)
```bash
make deploy-helm
```

## 4. Verification

```bash
# Interactive validation script
./scripts/validate-deployment.sh

# Manual Checks
kubectl get pods -n todo-app
curl http://todo.local
```

## 5. Troubleshooting & Operations

### Common Issues

**Pods Pending**:
- Check resources: `kubectl describe pod -n todo-app <pod-name>`
- Minikube might need more RAM: `minikube stop && minikube start --memory=4096`

**Ingress 404/Connection Refused**:
- Verify Tunnel: `minikube tunnel` (required on Mac/Windows)
- Check Ingress: `kubectl get ingress -n todo-app`

**Database Connection Errors**:
- Verify `DATABASE_URL` is correct and accessible from within the cluster
- Check Backend logs: `kubectl logs -l component=backend -n todo-app`

### AI-Assisted Operations

**kubectl-ai**:
Explain resources or errors:
```bash
kubectl ai "Why is the backend pod crashing?"
kubectl ai "Explain the ingress configuration"
```

**Gordon (Docker Desktop)**:
- Optimizing Dockerfiles: "Analyze backend/Dockerfile for size optimizations"
- Security scanning: "Scan image backend:latest for vulnerabilities"
```

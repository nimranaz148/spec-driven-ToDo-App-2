# Quickstart: Phase 4 Local Kubernetes Deployment

**Concept**: Local Cloud-Native Development Environment  
**Status**: Production Ready

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (5 minutes)](#quick-start-5-minutes)
3. [Manual Setup](#manual-setup)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)
6. [AI-Assisted Operations](#ai-assisted-operations)
7. [Advanced Topics](#advanced-topics)

---

## Prerequisites

Install the following tools before proceeding:

- **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** - Container runtime
- **[Minikube](https://minikube.sigs.k8s.io/docs/start/)** - Local Kubernetes cluster
- **[Helm](https://helm.sh/docs/intro/install/)** - Kubernetes package manager
- **[kubectl](https://kubernetes.io/docs/tasks/tools/)** - Kubernetes CLI

Verify installations:

```bash
docker --version
minikube version
helm version
kubectl version --client
```

### Environment Variables

Set up required secrets:

```bash
# Required
export DATABASE_URL="postgresql://user:pass@host.neon.tech:5432/neondb?sslmode=require"
export OPENAI_API_KEY="sk-your-openai-api-key"

# Optional (has defaults)
export BETTER_AUTH_SECRET="$(openssl rand -base64 32)"
export BETTER_AUTH_URL="http://todo.local"
```

---

## Quick Start (5 minutes)

One-command deployment using the Makefile:

```bash
# 1. Start Minikube
minikube start --driver=docker --memory=4096

# 2. Set environment variables (see above)
export DATABASE_URL="postgresql://..."
export OPENAI_API_KEY="sk-..."

# 3. Deploy everything
make k8s-setup

# 4. Configure DNS
echo "127.0.0.1 todo.local" | sudo tee -a /etc/hosts

# 5. Start tunnel (Mac/Windows - keep running in separate terminal)
minikube tunnel

# 6. Open browser
open http://todo.local
```

That's it! The application should now be running.

---

## Manual Setup

If you prefer step-by-step control:

### 1. Start Minikube

```bash
minikube start --driver=docker --memory=4096 --cpus=2

# Enable NGINX Ingress Controller
minikube addons enable ingress
```

### 2. Build Docker Images

Point Docker CLI to Minikube's daemon:

```bash
# Run this in every new terminal session
eval $(minikube docker-env)

# Build all images
docker build -t frontend:latest ./frontend
docker build -t backend:latest ./backend
docker build -t mcp:latest ./mcp

# Verify images
docker images | grep -E 'frontend|backend|mcp'
```

**Expected image sizes**:

- Frontend: < 200MB
- Backend: < 500MB
- MCP: < 500MB

### 3. Deploy with Helm

```bash
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --create-namespace \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY"
```

**OR** deploy with raw Kubernetes manifests:

```bash
# Create secrets manually
kubectl create namespace todo-app
kubectl create secret generic todo-secrets -n todo-app \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
  --from-literal=BETTER_AUTH_SECRET="$BETTER_AUTH_SECRET" \
  --from-literal=BETTER_AUTH_URL="$BETTER_AUTH_URL"

# Apply manifests
kubectl apply -f k8s/
```

### 4. Configure DNS

**Mac/Linux**:

```bash
echo "127.0.0.1 todo.local" | sudo tee -a /etc/hosts
```

**Windows** (as Administrator):

```powershell
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "127.0.0.1 todo.local"
```

**Alternative** (use Minikube IP):

```bash
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts
```

### 5. Expose Ingress (Mac/Windows)

On Mac/Windows, you need to run `minikube tunnel` to expose the Ingress:

```bash
# Run in a separate terminal and keep it running
minikube tunnel
```

**Linux users**: Skip this step, Ingress should work directly with Minikube IP.

---

## Verification

### Automated Validation

```bash
# Run comprehensive validation script
make validate

# OR
./scripts/validate-deployment.sh
```

This checks:

- ✅ All pods are Running
- ✅ Pod stability (0 restarts)
- ✅ Services exist
- ✅ Ingress configured
- ✅ Health endpoints responding
- ✅ Image sizes

### Manual Checks

```bash
# Check pod status (should see 5 pods: 2 backend, 2 frontend, 1 mcp)
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app

# Check ingress
kubectl get ingress -n todo-app

# Test backend health
kubectl port-forward -n todo-app svc/backend-service 8000:8000
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

# Test application
curl http://todo.local
# Should return HTML
```

### Access Application

Open your browser and navigate to:

```
http://todo.local
```

You should see the Todo Chatbot login page.

---

## Troubleshooting

### Common Issues

#### 1. Pods Pending/Not Starting

**Symptoms**: `kubectl get pods -n todo-app` shows Pending state

**Solutions**:

```bash
# Check pod events
kubectl describe pod -n todo-app <pod-name>

# Increase Minikube resources
minikube stop
minikube start --driver=docker --memory=6144 --cpus=4

# Check resource usage
kubectl top nodes
```

#### 2. ImagePullBackOff

**Symptoms**: Pods show ImagePullBackOff status

**Solutions**:

```bash
# Ensure you're using Minikube's Docker daemon
eval $(minikube docker-env)

# Rebuild images
make build-images

# Verify images exist
docker images | grep -E 'frontend|backend|mcp'

# Check imagePullPolicy is set to Never
kubectl get deployment -n todo-app backend -o yaml | grep imagePullPolicy
```

#### 3. Ingress 404/Connection Refused

**Symptoms**: `http://todo.local` returns 404 or connection refused

**Solutions**:

```bash
# Verify ingress addon is enabled
minikube addons list | grep ingress

# Enable if disabled
minikube addons enable ingress

# Mac/Windows: Start tunnel (must keep running)
minikube tunnel

# Check ingress status
kubectl get ingress -n todo-app
kubectl describe ingress -n todo-app todo-ingress

# Verify /etc/hosts entry
cat /etc/hosts | grep todo.local

# Test backend directly
kubectl port-forward -n todo-app svc/backend-service 8000:8000
curl http://localhost:8000/health
```

#### 4. Database Connection Errors

**Symptoms**: Backend pods crash with database connection errors

**Solutions**:

```bash
# Check backend logs
kubectl logs -n todo-app -l component=backend --tail=50

# Verify DATABASE_URL is set correctly
kubectl get secret todo-secrets -n todo-app -o jsonpath='{.data.DATABASE_URL}' | base64 -d

# Test database connectivity from pod
kubectl exec -it -n todo-app deployment/backend -- sh
# Inside pod:
python -c "import os; print(os.environ.get('DATABASE_URL'))"
```

#### 5. Pods Restarting

**Symptoms**: Pods show restart count > 0

**Solutions**:

```bash
# Check pod logs for errors
kubectl logs -n todo-app <pod-name> --previous

# Check resource limits
kubectl describe pod -n todo-app <pod-name> | grep -A 5 Limits

# Check liveness/readiness probes
kubectl describe pod -n todo-app <pod-name> | grep -A 10 Liveness
```

#### 6. Helm Deployment Failures

**Symptoms**: `helm install` fails

**Solutions**:

```bash
# Lint chart first
helm lint ./helm/todo-app

# Dry run to see what would be applied
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --dry-run \
  --debug \
  --set secrets.databaseUrl="test"

# Check existing releases
helm list -A

# Uninstall and retry
helm uninstall todo-app -n todo-app
make deploy-helm
```

### Debugging Commands

```bash
# Get all resources
kubectl get all -n todo-app

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Check logs for all components
kubectl logs -n todo-app -l app=todo-chatbot --tail=20

# Execute shell in pod
kubectl exec -it -n todo-app deployment/backend -- sh

# Port forward for local access
kubectl port-forward -n todo-app svc/frontend-service 3000:3000

# Get pod resource usage
kubectl top pods -n todo-app
```

---

## AI-Assisted Operations

### kubectl-ai (Kubernetes Copilot)

Install and use kubectl-ai for natural language queries:

```bash
# Installation
kubectl krew install ai

# Usage examples
kubectl ai "Why is the backend pod crashing?"
kubectl ai "Explain the ingress configuration"
kubectl ai "Show me high memory usage pods"
kubectl ai "How do I debug a CrashLoopBackOff?"
```

### kagent (Kubernetes Agent)

Automate complex operations:

```bash
# Example: Auto-scale based on custom metrics
kagent --task "Scale backend deployment if error rate > 5%"

# Example: Automated troubleshooting
kagent --task "Diagnose and fix pod startup issues"
```

### Gordon (Docker Desktop AI)

Use Docker Desktop's built-in AI assistant:

**Dockerfile Optimization**:

```
Gordon: "Analyze backend/Dockerfile for size optimizations"
Gordon: "Suggest multi-stage build improvements"
```

**Security Scanning**:

```
Gordon: "Scan image backend:latest for vulnerabilities"
Gordon: "What security best practices am I missing?"
```

**Container Debugging**:

```
Gordon: "Why is my container using so much memory?"
Gordon: "Optimize container startup time"
```

---

## Advanced Topics

### Resource Management

Adjust resource limits in Helm values:

```yaml
# values-custom.yaml
resources:
  backend:
    limits:
      memory: 1Gi
      cpu: "2"
    requests:
      memory: 512Mi
      cpu: "1"
```

Deploy with custom values:

```bash
helm upgrade todo-app ./helm/todo-app \
  --namespace todo-app \
  --values values-custom.yaml
```

### Horizontal Pod Autoscaling

```bash
# Enable metrics server
minikube addons enable metrics-server

# Create HPA
kubectl autoscale deployment backend -n todo-app \
  --cpu-percent=70 \
  --min=2 \
  --max=5

# Check HPA status
kubectl get hpa -n todo-app
```

### Persistent Storage

For development with local data:

```yaml
# Add to backend-deployment.yaml
volumeMounts:
  - name: local-data
    mountPath: /app/data
volumes:
  - name: local-data
    hostPath:
      path: /data/todo-app
      type: DirectoryOrCreate
```

### Production Deployment

For production Kubernetes clusters:

1. Change `imagePullPolicy` to `IfNotPresent` or `Always`
2. Push images to a container registry (Docker Hub, ECR, GCR)
3. Update `values.yaml` with registry paths
4. Configure TLS/SSL for ingress
5. Set up proper secrets management (Sealed Secrets, Vault)
6. Configure monitoring (Prometheus, Grafana)

---

## Cleanup

### Remove Application

```bash
# Using Makefile
make teardown

# Using Helm
helm uninstall todo-app -n todo-app

# Delete namespace
kubectl delete namespace todo-app
```

### Stop Minikube

```bash
# Stop cluster
minikube stop

# Delete cluster (removes all data)
minikube delete
```

---

## Next Steps

- **Monitoring**: Set up Prometheus and Grafana
- **Logging**: Configure EFK stack (Elasticsearch, Fluentd, Kibana)
- **CI/CD**: Integrate with GitHub Actions for automated deployments
- **Production**: Migrate to managed Kubernetes (EKS, GKE, AKS)

For more details, see:

- [Helm Chart README](../../helm/todo-app/README.md)
- [Deployment Documentation](../../docs/deployment.md)
- [Main README](../../README.md)

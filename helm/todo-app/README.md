# Todo App Helm Chart

A Helm chart for deploying the Todo Chatbot Application to Kubernetes (Minikube).

## Prerequisites

- Kubernetes cluster (Minikube recommended)
- Helm 3.x
- kubectl configured to access your cluster
- Docker images built locally (see Build Instructions below)

## Build Docker Images

Before installing the chart, build the Docker images in Minikube's Docker environment:

```bash
# Set up Minikube Docker environment
eval $(minikube docker-env)

# Build all images
docker build -t frontend:latest ./frontend
docker build -t backend:latest ./backend
docker build -t mcp:latest ./mcp
```

## Installation

### Quick Install (with required secrets)

```bash
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --create-namespace \
  --set secrets.databaseUrl="postgresql://user:password@host:5432/dbname?sslmode=require" \
  --set secrets.openaiApiKey="your-openai-api-key"
```

### Install with Custom Values File

```bash
# Create your own values file
cp helm/todo-app/values-dev.yaml my-values.yaml

# Edit my-values.yaml with your configuration
# Then install:
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --create-namespace \
  --values my-values.yaml
```

### Using Environment Variables

```bash
# Load secrets from environment
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --create-namespace \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET"
```

## Configuration

### Values

| Parameter                          | Description                  | Default                |
| ---------------------------------- | ---------------------------- | ---------------------- |
| `environment`                      | Environment name             | `local`                |
| `images.frontend.repository`       | Frontend image repository    | `frontend`             |
| `images.frontend.tag`              | Frontend image tag           | `latest`               |
| `images.frontend.pullPolicy`       | Frontend image pull policy   | `Never`                |
| `images.backend.repository`        | Backend image repository     | `backend`              |
| `images.backend.tag`               | Backend image tag            | `latest`               |
| `images.backend.pullPolicy`        | Backend image pull policy    | `Never`                |
| `images.mcp.repository`            | MCP image repository         | `mcp`                  |
| `images.mcp.tag`                   | MCP image tag                | `latest`               |
| `images.mcp.pullPolicy`            | MCP image pull policy        | `Never`                |
| `replicas.frontend`                | Number of frontend replicas  | `2`                    |
| `replicas.backend`                 | Number of backend replicas   | `2`                    |
| `replicas.mcp`                     | Number of MCP replicas       | `1`                    |
| `resources.frontend.limits.memory` | Frontend memory limit        | `256Mi`                |
| `resources.frontend.limits.cpu`    | Frontend CPU limit           | `0.5`                  |
| `resources.backend.limits.memory`  | Backend memory limit         | `512Mi`                |
| `resources.backend.limits.cpu`     | Backend CPU limit            | `1`                    |
| `resources.mcp.limits.memory`      | MCP memory limit             | `256Mi`                |
| `resources.mcp.limits.cpu`         | MCP CPU limit                | `0.5`                  |
| `ingress.enabled`                  | Enable ingress               | `true`                 |
| `ingress.host`                     | Ingress host                 | `todo.local`           |
| `ingress.ingressClassName`         | Ingress class                | `nginx`                |
| `config.nodeEnv`                   | Node environment             | `production`           |
| `config.logLevel`                  | Log level                    | `info`                 |
| `secrets.databaseUrl`              | PostgreSQL connection string | `""` (required)        |
| `secrets.betterAuthSecret`         | Better Auth secret           | `secure-random-string` |
| `secrets.betterAuthUrl`            | Better Auth URL              | `http://todo.local`    |
| `secrets.openaiApiKey`             | OpenAI API key               | `""` (required)        |

### Required Secrets

The following secrets must be provided:

1. **DATABASE_URL**: PostgreSQL connection string (Neon DB recommended)

   ```
   postgresql://user:password@host:5432/dbname?sslmode=require
   ```

2. **OPENAI_API_KEY**: Your OpenAI API key for the chatbot functionality

3. **BETTER_AUTH_SECRET**: A secure random string (optional, has default)

## Post-Installation

### Enable NGINX Ingress

```bash
minikube addons enable ingress
```

### Configure /etc/hosts

Add the following entry to your `/etc/hosts` file (or `C:\Windows\System32\drivers\etc\hosts` on Windows):

```
127.0.0.1 todo.local
```

Or use Minikube's IP:

```bash
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts
```

### Verify Installation

```bash
# Check all pods are running
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app

# Check ingress
kubectl get ingress -n todo-app

# Test health endpoints
kubectl port-forward -n todo-app svc/backend-service 8000:8000
curl http://localhost:8000/health
```

### Access the Application

Open your browser and navigate to:

```
http://todo.local
```

## Upgrading

```bash
# Upgrade with new values
helm upgrade todo-app ./helm/todo-app \
  --namespace todo-app \
  --set secrets.databaseUrl="$DATABASE_URL"

# Or with values file
helm upgrade todo-app ./helm/todo-app \
  --namespace todo-app \
  --values my-values.yaml
```

## Uninstallation

```bash
# Uninstall the release
helm uninstall todo-app --namespace todo-app

# Delete the namespace
kubectl delete namespace todo-app
```

## Troubleshooting

### Pods not starting

```bash
# Check pod status
kubectl get pods -n todo-app

# Check pod logs
kubectl logs -n todo-app <pod-name>

# Describe pod for events
kubectl describe pod -n todo-app <pod-name>
```

### Image pull errors

If you see `ImagePullBackOff` errors, ensure:

1. You're using Minikube's Docker environment: `eval $(minikube docker-env)`
2. Images are built locally
3. `imagePullPolicy: Never` is set in values

### Database connection issues

```bash
# Check backend logs
kubectl logs -n todo-app -l component=backend

# Verify secrets are correctly set
kubectl get secret -n todo-app todo-secrets -o yaml
```

### Ingress not working

```bash
# Verify ingress addon is enabled
minikube addons list | grep ingress

# Enable if disabled
minikube addons enable ingress

# Check ingress status
kubectl get ingress -n todo-app
kubectl describe ingress -n todo-app todo-ingress
```

## Development

### Linting

```bash
# Validate chart syntax
helm lint ./helm/todo-app

# Render templates to verify output
helm template todo-app ./helm/todo-app \
  --set secrets.databaseUrl="test" \
  --set secrets.openaiApiKey="test"
```

### Testing

```bash
# Dry run installation
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --create-namespace \
  --dry-run \
  --debug \
  --set secrets.databaseUrl="test" \
  --set secrets.openaiApiKey="test"
```

## Support

For issues and questions, refer to:

- [Quickstart Guide](../../specs/001-local-kubernetes/quickstart.md)
- [Main README](../../README.md)
- [Deployment Documentation](../../docs/deployment.md)

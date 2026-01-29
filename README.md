# Todo App: Cloud-Native Task Management with AI Chatbot

A full-stack todo application with an integrated AI chatbot for natural language task management. Deployed on local Kubernetes (Minikube) with production-ready patterns.

## Features

- ✅ **Task Management**: Create, update, delete, and organize tasks
- 🤖 **AI Chatbot**: Natural language interface powered by OpenAI
- 🔐 **Authentication**: Secure user auth with Better Auth
- 🎨 **Modern UI**: Next.js 14 with Tailwind CSS and shadcn/ui
- ⚡ **Fast API**: FastAPI backend with PostgreSQL (Neon DB)
- 🚀 **Cloud Native**: Kubernetes deployment with Helm charts
- 📊 **Observability**: Structured logging and health checks

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) - Container runtime
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) - Local Kubernetes
- [Helm](https://helm.sh/docs/intro/install/) - Kubernetes package manager
- [kubectl](https://kubernetes.io/docs/tasks/tools/) - Kubernetes CLI

### 5-Minute Deployment

```bash
# 1. Start Minikube
minikube start --driver=docker --memory=4096

# 2. Set environment variables
export DATABASE_URL="postgresql://user:pass@host.neon.tech:5432/db?sslmode=require"
export OPENAI_API_KEY="sk-your-openai-api-key"

# 3. Deploy everything (builds images + installs with Helm)
make k8s-setup

# 4. Configure DNS (one-time)
echo "127.0.0.1 todo.local" | sudo tee -a /etc/hosts

# 5. Start tunnel (Mac/Windows only - keep running)
minikube tunnel

# 6. Open application
open http://todo.local
```

For detailed instructions, see the [Quickstart Guide](specs/001-local-kubernetes/quickstart.md).

## Architecture

### Technology Stack

**Frontend**:

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS + shadcn/ui
- Better Auth for authentication
- AI SDK for chatbot integration

**Backend**:

- FastAPI (Python)
- PostgreSQL (Neon DB)
- SQLAlchemy ORM
- Alembic migrations
- Pydantic validation

**Infrastructure**:

- Kubernetes (Minikube)
- Helm for deployment
- NGINX Ingress Controller
- Docker multi-stage builds

**AI/MCP**:

- OpenAI GPT-4
- Model Context Protocol (MCP) Server
- Custom tools for task management

### Service Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP
       ↓
┌─────────────────┐
│ NGINX Ingress   │
│  (todo.local)   │
└────┬───────┬────┘
     │       │
     │       └──────────────┐
     ↓                      ↓
┌──────────┐        ┌──────────┐
│ Frontend │        │ Backend  │
│ (Next.js)│───────→│ (FastAPI)│
└──────────┘        └────┬─────┘
     2 replicas          │
                         ↓
                    ┌─────────┐
                    │   MCP   │
                    │ Server  │
                    └────┬────┘
                         │
                         ↓
                    ┌──────────┐
                    │ Neon DB  │
                    │(Postgres)│
                    └──────────┘
```

## Directory Structure

```
.
├── frontend/           # Next.js frontend application
│   ├── src/
│   ├── public/
│   ├── Dockerfile
│   └── package.json
├── backend/            # FastAPI backend application
│   ├── src/
│   ├── tests/
│   ├── migrations/     # Alembic database migrations
│   ├── Dockerfile
│   └── pyproject.toml
├── mcp/                # MCP Server deployment
│   └── Dockerfile
├── k8s/                # Raw Kubernetes manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml.template
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── mcp-deployment.yaml
│   └── ingress.yaml
├── helm/               # Helm charts
│   └── todo-app/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-dev.yaml
│       ├── templates/
│       └── README.md
├── scripts/            # Deployment & utility scripts
│   ├── deploy-backend.sh
│   ├── validate-deployment.sh
│   └── teardown.sh
├── specs/              # Project specifications
│   └── 001-local-kubernetes/
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       └── quickstart.md
├── docs/               # Additional documentation
├── Makefile            # Development & deployment commands
└── README.md           # This file
```

## Development

### Local Development (without Kubernetes)

Run services locally for rapid development:

```bash
# Install dependencies
make install

# Run all services (in separate terminals)
make backend-dev    # Terminal 1: Backend API (port 8000)
make mcp-dev        # Terminal 2: MCP Server (port 8001)
make frontend-dev   # Terminal 3: Frontend (port 3000)

# Or run all in background
make chat-dev-bg

# Stop all services
make stop
```

### Testing

```bash
# Run all tests
make test

# Backend tests only
make test-backend

# Frontend tests only
make test-frontend
```

### Kubernetes Deployment

```bash
# Build Docker images for Minikube
make build-images

# Deploy with raw manifests
make deploy-k8s

# Deploy with Helm
make deploy-helm

# Validate deployment
make validate

# Teardown
make teardown
```

## Configuration

### Environment Variables

Create `.env` files or set environment variables:

**Required**:

- `DATABASE_URL`: PostgreSQL connection string (Neon DB)
- `OPENAI_API_KEY`: OpenAI API key

**Optional**:

- `BETTER_AUTH_SECRET`: Authentication secret (auto-generated if not set)
- `BETTER_AUTH_URL`: Base URL for auth callbacks (default: `http://todo.local`)
- `NODE_ENV`: Environment (`development` or `production`)
- `LOG_LEVEL`: Logging level (`debug`, `info`, `warning`, `error`)

### Helm Values

Customize deployment by editing `helm/todo-app/values.yaml` or creating a custom values file:

```yaml
# custom-values.yaml
replicas:
  backend: 3
  frontend: 3

resources:
  backend:
    limits:
      memory: 1Gi
      cpu: "2"

ingress:
  host: myapp.local
```

Deploy with custom values:

```bash
helm upgrade todo-app ./helm/todo-app --values custom-values.yaml
```

## Makefile Commands

| Command             | Description                     |
| ------------------- | ------------------------------- |
| `make install`      | Install all dependencies        |
| `make backend-dev`  | Run backend API server          |
| `make mcp-dev`      | Run MCP server                  |
| `make frontend-dev` | Run frontend dev server         |
| `make chat-dev-bg`  | Run all services in background  |
| `make stop`         | Stop all background services    |
| `make test`         | Run all tests                   |
| `make build-images` | Build Docker images in Minikube |
| `make deploy-k8s`   | Deploy with raw K8s manifests   |
| `make deploy-helm`  | Deploy with Helm chart          |
| `make k8s-setup`    | Build + deploy (one command)    |
| `make validate`     | Validate K8s deployment         |
| `make teardown`     | Clean up K8s resources          |
| `make clean`        | Clean logs and temp files       |

## Documentation

- **[Quickstart Guide](specs/001-local-kubernetes/quickstart.md)** - Deployment instructions
- **[Helm Chart README](helm/todo-app/README.md)** - Helm chart documentation
- **[API Documentation](docs/api.md)** - Backend API reference
- **[Deployment Guide](docs/deployment.md)** - Production deployment
- **[Security Architecture](backend/SECURITY_ARCHITECTURE.md)** - Security patterns

## Troubleshooting

### Common Issues

**Pods not starting**: Check Minikube has enough resources

```bash
minikube stop
minikube start --memory=6144 --cpus=4
```

**ImagePullBackOff**: Ensure using Minikube's Docker daemon

```bash
eval $(minikube docker-env)
make build-images
```

**Ingress 404**: Start Minikube tunnel (Mac/Windows)

```bash
minikube tunnel  # Keep running
```

**Database connection errors**: Verify DATABASE_URL

```bash
kubectl logs -n todo-app -l component=backend
```

For more troubleshooting, see [Quickstart Guide - Troubleshooting](specs/001-local-kubernetes/quickstart.md#troubleshooting).

## AI-Assisted Operations

### kubectl-ai

Natural language Kubernetes queries:

```bash
kubectl ai "Why is the backend pod crashing?"
kubectl ai "Show me high memory usage pods"
```

### Gordon (Docker Desktop)

Dockerfile optimization and security:

```
Gordon: "Analyze backend/Dockerfile for size optimizations"
Gordon: "Scan image backend:latest for vulnerabilities"
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:

- 📖 Check the [Quickstart Guide](specs/001-local-kubernetes/quickstart.md)
- 🐛 Open an issue on GitHub
- 📧 Contact the development team

---

**Built with ❤️ using Spec-Driven Development**

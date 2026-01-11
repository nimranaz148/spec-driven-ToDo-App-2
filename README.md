# Todo App Phase 4: Local Kubernetes Deployment

This repository contains the Todo App application with support for local Kubernetes deployment using Minikube and Helm.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [Helm](https://helm.sh/docs/intro/install/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

## Getting Started

See [Quickstart Guide](specs/001-local-kubernetes/quickstart.md) for detailed deployment instructions.

## Directory Structure

- `frontend/`: Next.js frontend application
- `backend/`: FastAPI backend application
- `mcp/`: MCP Server artifacts
- `k8s/`: Kubernetes manifests
- `helm/`: Helm charts
- `specs/`: Project specifications and documentation

## Development

1. Start Minikube: `minikube start --driver=docker`
2. Enable Ingress: `minikube addons enable ingress`
3. Deploy with Helm: `helm install todo-app ./helm/todo-app`

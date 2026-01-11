#\!/bin/bash
set -e

# Build images
echo "Building Docker images..."
eval $(minikube docker-env)
docker build -t backend:latest ./backend
docker build -t mcp:latest -f mcp/Dockerfile .
docker build -t frontend:latest ./frontend

# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets if not exists
if \! kubectl get secret todo-secrets -n todo-app &> /dev/null; then
  echo "Creating default secrets from template..."
  if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL environment variable not set"
    exit 1
  fi
  sed "s|DATABASE_URL:.*|DATABASE_URL: $DATABASE_URL|g" k8s/secrets.yaml.template > k8s/secrets.yaml
  kubectl apply -f k8s/secrets.yaml
fi

# Apply manifests
echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/mcp-deployment.yaml
kubectl apply -f k8s/mcp-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
kubectl apply -f k8s/ingress.yaml

echo "Deployment complete\! Waiting for pods..."
kubectl wait --for=condition=ready pod -l app=todo-chatbot -n todo-app --timeout=300s


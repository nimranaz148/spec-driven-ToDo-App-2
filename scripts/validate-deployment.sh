#\!/bin/bash
set -e

echo "Starting deployment validation..."

# 1. Check all pods are Running
echo "Checking pod status..."
# Wait up to 5 minutes for pods to be ready
if kubectl wait --for=condition=ready pod -l app=todo-chatbot -n todo-app --timeout=300s; then
    echo "✅ All pods are ready"
else
    echo "❌ Timeout waiting for pods to be ready"
    kubectl get pods -n todo-app
    exit 1
fi

# 2. Check service existence
echo "Checking services..."
REQUIRED_SVCS=("backend-service" "mcp-service" "frontend-service")
for svc in "${REQUIRED_SVCS[@]}"; do
    if kubectl get svc $svc -n todo-app > /dev/null 2>&1; then
        echo "✅ Service $svc exists"
    else
        echo "❌ Service $svc not found"
        exit 1
    fi
done

# 3. Check Ingress accessible
echo "Checking Ingress..."
if kubectl get ingress todo-ingress -n todo-app > /dev/null 2>&1; then
    echo "✅ Ingress exists"
else
    echo "❌ Ingress not found"
    exit 1
fi

# 4. Check Backend Health
echo "Checking Backend Health..."
# Use port-forward in background
kubectl port-forward -n todo-app svc/backend-service 8000:8000 > /dev/null 2>&1 &
PF_PID=$\!
sleep 5
if curl -s -f http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    kill $PF_PID
    exit 1
fi
kill $PF_PID

echo "🎉 Deployment validation passed successfully\!"


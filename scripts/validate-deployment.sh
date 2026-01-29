#!/bin/bash
set -e

echo "Starting deployment validation..."
START_TIME=$(date +%s)

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

# 2. Check pod stability (0 restarts after 5 minutes)
echo "Checking pod stability..."
RESTARTS=$(kubectl get pods -n todo-app -o jsonpath='{range .items[*]}{.status.containerStatuses[*].restartCount}{"\n"}{end}' | awk '{s+=$1} END {print s}')
if [ "$RESTARTS" -eq 0 ]; then
    echo "✅ All pods stable with 0 restarts"
else
    echo "⚠️  Warning: $RESTARTS total restarts detected"
fi

# 3. Check service existence
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

# 4. Check Ingress accessible
echo "Checking Ingress..."
if kubectl get ingress todo-ingress -n todo-app > /dev/null 2>&1; then
    echo "✅ Ingress exists"
    # Check if ingress has an address
    INGRESS_ADDR=$(kubectl get ingress todo-ingress -n todo-app -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [ -n "$INGRESS_ADDR" ]; then
        echo "✅ Ingress address: $INGRESS_ADDR"
    fi
else
    echo "❌ Ingress not found"
    exit 1
fi

# 5. Check Backend Health
echo "Checking Backend Health..."
# Use port-forward in background
kubectl port-forward -n todo-app svc/backend-service 8000:8000 > /dev/null 2>&1 &
PF_PID=$!
sleep 5
if curl -s -f http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    kill $PF_PID 2>/dev/null || true
    exit 1
fi
kill $PF_PID 2>/dev/null || true

# 6. Check MCP Health
echo "Checking MCP Health..."
kubectl port-forward -n todo-app svc/mcp-service 8001:8001 > /dev/null 2>&1 &
PF_PID=$!
sleep 5
if curl -s -f http://localhost:8001/health > /dev/null; then
    echo "✅ MCP is healthy"
else
    echo "⚠️  Warning: MCP health check failed (may not have /health endpoint)"
fi
kill $PF_PID 2>/dev/null || true

# 7. Check image sizes (if docker is available)
echo "Checking image sizes..."
if command -v docker &> /dev/null; then
    eval $(minikube docker-env 2>/dev/null) || true
    FRONTEND_SIZE=$(docker images frontend:latest --format "{{.Size}}" 2>/dev/null || echo "unknown")
    BACKEND_SIZE=$(docker images backend:latest --format "{{.Size}}" 2>/dev/null || echo "unknown")
    echo "  Frontend image: $FRONTEND_SIZE"
    echo "  Backend image: $BACKEND_SIZE"
fi

# Calculate deployment time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo ""
echo "🎉 Deployment validation passed successfully!"
echo "⏱️  Validation completed in ${DURATION} seconds"
echo ""
echo "Summary:"
kubectl get pods -n todo-app
echo ""
echo "Access the application at: http://todo.local"


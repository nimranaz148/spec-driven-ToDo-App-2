#\!/bin/bash
echo "Tearing down Todo App deployment..."

# Delete namespace (including all resources within it)
kubectl delete namespace todo-app --ignore-not-found=true

# Wait for deletion
echo "Waiting for namespace deletion..."
kubectl wait --for=delete namespace/todo-app --timeout=60s || true

echo "✅ Teardown complete"


#!/bin/bash
echo "Tearing down Todo App deployment..."

# Check if namespace exists
if kubectl get namespace todo-app &> /dev/null; then
    echo "Found todo-app namespace, deleting..."
    
    # Delete namespace (including all resources within it)
    kubectl delete namespace todo-app --timeout=120s
    
    # Wait for deletion
    echo "Waiting for namespace deletion..."
    kubectl wait --for=delete namespace/todo-app --timeout=60s 2>/dev/null || true
    
    echo "✅ Namespace deleted"
else
    echo "ℹ️  Namespace todo-app does not exist"
fi

# Clean up Helm releases if any exist
if command -v helm &> /dev/null; then
    if helm list -n todo-app 2>/dev/null | grep -q todo-app; then
        echo "Found Helm release, uninstalling..."
        helm uninstall todo-app -n todo-app 2>/dev/null || true
    fi
fi

echo "✅ Teardown complete"
echo ""
echo "Note: Minikube itself is still running. To stop it:"
echo "  minikube stop"
echo "To delete the entire Minikube cluster:"
echo "  minikube delete"


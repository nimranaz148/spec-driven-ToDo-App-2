# Blueprints Examples

## Example 1: Defining a Frontend Deployment Spec

Create a file `specs/infra/frontend-deployment.md`:

```markdown
# Frontend Deployment Spec

## Requirements
- Image: todo-frontend:latest
- Replicas: 2
- Port: 3000
- Env Vars:
  - NEXT_PUBLIC_API_URL: http://backend:8000
- Resources:
  - Requests: 100m CPU, 128Mi Memory
  - Limits: 500m CPU, 512Mi Memory
```

## Example 2: Generating Manifests from Spec

Use the blueprint skill to generate K8s manifests:

"Using the blueprints skill, generate a Kubernetes Deployment and Service for the @specs/infra/frontend-deployment.md spec."

## Example 3: Creating a Helm Chart Blueprint

"Based on the standard stateless service pattern in blueprints, create a Helm chart structure for the backend API."

# Phase 4 Implementation Plan Prompt

Use this file to guide the autonomous agent in generating the implementation plan for Phase 4.

## Feature Context
**Project**: Evolution of Todo
**Phase**: Phase 4 - Local Kubernetes Deployment
**Feature**: `001-local-kubernetes`
**Spec**: `specs/001-local-kubernetes/spec.md`

## Plan Generation Instructions
When running `/sp.plan`, use the contents of `specs/001-local-kubernetes/spec.md` as the primary input.

## Key Architecture Decisions
- **Orchestration**: Minikube (Local)
- **Deployment**: Hybrid approach (Raw Manifests for dev/learning, Helm Charts for prod/ops)
- **Service Exposure**: NodePort (Dev), Ingress (Routing)
- **Registry**: Docker Hub (Dev), GHCR (Prod - future)

## Required Artifacts
1. **research.md**: Document the architecture decisions above.
2. **data-model.md**: Define K8s resources (Deployments, Services, ConfigMaps).
3. **quickstart.md**: Provide `minikube start`, `docker build`, and `kubectl apply` commands.
4. **contracts/**: Define Helm Values schema.
5. **plan.md**: Comprehensive implementation strategy including "Infrastructure as Code" and "Multi-Stage Builds".

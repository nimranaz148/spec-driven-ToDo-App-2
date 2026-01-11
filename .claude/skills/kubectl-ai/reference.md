# Kubectl AI Reference

## Overview
`kubectl-ai` is a plugin for kubectl that generates and applies Kubernetes manifests using OpenAI GPT.

## Command Syntax
```bash
kubectl-ai "natural language prompt"
```

## Supported Operations
- **Generate**: Create new resources (deployment, service, ingress)
- **Modify**: Update existing resources (scale, change image)
- **Inspect**: Query the cluster state
- **Debug**: Analyze logs and status

## Flags
- `--require-confirmation`: Review changes before applying (Recommended)
- `--debug`: Enable debug logging

---
id: "0007"
title: "Create AIOps Helm Builder Agent"
stage: "misc"
date: "2026-01-12"
surface: "agent"
model: "claude-opus-4-5-20251101"
feature: "none"
branch: "001-local-kubernetes"
user: "USER"
command: "create-agent"
labels: ["helm", "agent", "kubernetes", "aiops"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - ".claude/agents/aiops-helm-builder.md"
tests: []
prompt_text: |
  mera ak helm-chart ka sub agent bna do or isko as a refrence use krlo...
response_text: |
  Created the aiops-helm-builder agent at .claude/agents/aiops-helm-builder.md. Verified available skills (helm, kubectl-ai, kagent) and updated the agent configuration accordingly.
outcome: "success"
evaluation: "Agent created successfully with correct skill configuration."
---

# Create AIOps Helm Builder Agent

## User Request
The user requested the creation of a Helm chart sub-agent (`aiops-helm-builder`) using a provided reference template.

## Execution
1. Verified available skills in `.claude/skills/`.
2. Created `.claude/agents/aiops-helm-builder.md` using the provided content but with corrected skill names (`helm`, `kubectl-ai`, `kagent`).

## Key Decisions
- The user provided `helm-charts-setup` and `kubectl-ai-setup` as skills, but I replaced them with the actual existing skills `helm`, `kubectl-ai`, and `kagent` after verifying the `.claude/skills/` directory.

## Outcome
The agent is now available for use in the project.

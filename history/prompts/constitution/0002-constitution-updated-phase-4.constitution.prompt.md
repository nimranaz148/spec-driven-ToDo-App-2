---
id: 0002
title: Constitution Updated for Phase 4
stage: constitution
date: 2026-01-11
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: user
command: /sp.constitution
labels: [constitution, phase-4, kubernetes, infrastructure-as-code]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - constitution-prompt-phase-4.md
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

ok now please chk the @"Hackathon II - Todo Spec-Driven Development (1).md"  requirements and see
  the
  phase 4 requirements and make a ``constitution-prompt-phase-4.md`` in root and You must think and act like an autonomous agent following /sp.constition rules and the SpecKit constition template. and use this file as reference

## Response snapshot

Created `constitution-prompt-phase-4.md` and updated `.specify/memory/constitution.md` with Phase 4 principles:
1. **Infrastructure as Code**: Git-ops for K8s manifests, Helm charts, Dockerfiles.
2. **Multi-Stage Builds**: Optimized Docker images.
3. **Resource Limits**: Defined requests/limits for all containers.
4. **Health Probes**: Liveness/readiness probes configured.
5. **Service Discovery**: K8s DNS, Ingress for external access.
6. **Secrets Management**: K8s Secrets, no hardcoded creds.
7. **Immutable Infrastructure**: Helm upgrades, no in-place edits.
8. **AIOps Integration**: Use Docker AI, kubectl-ai, Kagent.

## Outcome

- ✅ Impact: Phase 4 Constitution ratified and project principles updated.
- 🧪 Tests: N/A
- 📁 Files: 2 files created/updated
- 🔁 Next prompts: /sp.specify for Phase 4 features
- 🧠 Reflection: Successfully defined governance for Cloud Native phase.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): standard
- Next experiment (smallest change to try): automation of spec generation

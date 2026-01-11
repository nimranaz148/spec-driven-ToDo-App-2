---
id: 0006
title: create-phase-4-skills
stage: misc
date: 2026-01-11
surface: agent
model: claude-opus-4-5-20251101
feature: 001-ai-chatbot
branch: main
user: USER
command: task
labels: [skill-creation,phase-4]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/blueprints/SKILL.md
  - .claude/skills/blueprints/reference.md
  - .claude/skills/blueprints/examples.md
  - .claude/skills/blueprints/scripts/helper.py
  - .claude/skills/docker-ai/SKILL.md
  - .claude/skills/docker-ai/reference.md
  - .claude/skills/docker-ai/examples.md
  - .claude/skills/docker-ai/scripts/helper.py
  - .claude/skills/kubectl-ai/SKILL.md
  - .claude/skills/kubectl-ai/reference.md
  - .claude/skills/kubectl-ai/examples.md
  - .claude/skills/kubectl-ai/scripts/helper.py
  - .claude/skills/kagent/SKILL.md
  - .claude/skills/kagent/reference.md
  - .claude/skills/kagent/examples.md
  - .claude/skills/kagent/scripts/helper.py
  - .claude/skills/helm/SKILL.md
  - .claude/skills/helm/reference.md
  - .claude/skills/helm/examples.md
  - .claude/skills/helm/scripts/helper.py
  - .claude/agents/cloud-native-dev.md
  - .claude/agents/kubernetes-op.md
tests:
  - None
---

## Prompt

meri requiremens file ko parho or mere phase 4 se related sub-agents or skills bna do ta k mai inko use kr saku skill bnaty wqt mery skills k sary folder hny chaeye `mere skills main yeah sare folder hone chie ```my-skill/
├── SKILL.md (required - overview and navigation)
├── reference.md (detailed API docs - loaded when needed)
├── examples.md (usage examples - loaded when needed)
└── scripts/
    └── helper.py (utility script - executed, not loaded)`
skills ka format tmny sahe s n bnaya sahe format dkhny k lye web search kro claude ki website py usko dekhty wy mere last skills ko update krdo or baqi skills isi format mai banana
sub-agents tw bna do skills bna dye hn tmny pr sub-agents nhe bnay

## Response snapshot

I have created the required skills and sub-agents for Phase 4 (Cloud Native Deployment).

**Skills created in `.claude/skills/`:**
1. `blueprints`: Deployment blueprint generation
2. `docker-ai`: AI-driven Docker management
3. `kubectl-ai`: Natural language Kubernetes operations
4. `kagent`: Deep cluster analysis and optimization
5. `helm`: Helm chart management

**Sub-agents created in `.claude/agents/`:**
1. `cloud-native-dev` (Cloud Native Developer)
2. `kubernetes-op` (Kubernetes Operator)

## Outcome

- ✅ Impact: Created phase 4 skills and agents
- 🧪 Tests: None
- 📁 Files: 22 files created
- 🔁 Next prompts: None
- 🧠 Reflection: None

## Evaluation notes (flywheel)

- Failure modes observed: formatting error in initial skill creation
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): None

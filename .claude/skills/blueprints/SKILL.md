---
name: blueprints
description: Create and use deployment blueprints for cloud-native applications. Use when defining deployment strategies and generating infrastructure-as-code from specs.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

# Cloud-Native Deployment Blueprints

## Quick Reference
This skill provides reusable Spec-Driven Development deployment blueprints for cloud-native applications. It focuses on generating standardized deployment configurations for Kubernetes, Helm, and other cloud-native technologies based on specifications.

## Basic Setup
Ensure you have the Spec-Kit context loaded and a valid spec file to work with.
This skill works best when used in conjunction with `kubectl-ai` and `helm` skills.

## Core Patterns

### 1. Analyze Spec for Infrastructure
Use this skill to analyze a feature spec and determine the necessary infrastructure components (Deployment, Service, Ingress, PVC, etc.).

### 2. Generate Manifests
Generate Kubernetes manifests based on standard patterns defined in `reference.md`.

### 3. Blueprint Selection
The skill helps select the right blueprint (Stateless, Stateful, Job, CronJob) based on the application requirements.

## Usage
- See `examples.md` for detailed usage scenarios.
- See `reference.md` for blueprint definitions.

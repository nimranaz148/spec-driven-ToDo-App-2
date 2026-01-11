---
name: helm
description: Create and manage Helm charts for Kubernetes deployments. Use when packaging applications for deployment.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

# Helm Chart Management

## Quick Reference
This skill assists in creating, managing, and deploying Helm charts. It helps standardize deployments by leveraging templates and value configurations.

## Basic Setup
- Install `helm` CLI.
- Initialize a chart using `helm create` or start from a blueprint.

## Core Patterns

### 1. Chart Creation
Generate the standard directory structure and boilerplate files for a new Helm chart.

### 2. Value Management
Configure `values.yaml` to parameterize deployments for different environments (dev, staging, prod).

### 3. Release Management
Install, upgrade, and rollback releases using Helm.

## Usage
- See `examples.md` for command usage.
- See `reference.md` for chart structure and concepts.

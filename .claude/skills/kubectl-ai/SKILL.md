---
name: kubectl-ai
description: Intelligent Kubernetes operations using the kubectl-ai plugin. Use when generating, applying, or debugging Kubernetes resources via natural language.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

# Kubectl AI Management

## Quick Reference
This skill integrates `kubectl-ai` to perform Kubernetes operations using natural language. It allows you to generate manifests, modify resources, and debug clusters without remembering verbose kubectl commands.

## Basic Setup
- Install `kubectl-ai` plugin.
- Configure OpenAI API key for the plugin.
- Ensure `kubectl` is configured with a valid context (Minikube or Cloud).

## Core Patterns

### 1. Generative Operations
Create complex Kubernetes resources using simple English descriptions.

### 2. Interactive Changes
Review generated manifests before they are applied to the cluster.

### 3. Cluster Inspection
Ask questions about the current state of the cluster.

## Usage
- See `examples.md` for prompt examples.
- See `reference.md` for command syntax.

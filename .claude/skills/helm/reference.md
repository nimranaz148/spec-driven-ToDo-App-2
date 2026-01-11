# Helm Reference

## Overview
Helm is the package manager for Kubernetes. This skill helps in creating, managing, and deploying Helm charts.

## Key Concepts
- **Chart**: A collection of files that describe a related set of Kubernetes resources.
- **Values**: Configuration for the chart.
- **Release**: A running instance of a chart.

## Directory Structure
```
mychart/
  Chart.yaml          # A YAML file containing information about the chart
  values.yaml         # The default configuration values for this chart
  charts/             # A directory containing any charts upon which this chart depends
  templates/          # A directory of templates that, when combined with values,
                      # will generate valid Kubernetes manifest files.
```

## Common Commands
- `helm create <name>`: Create a new chart
- `helm install <release> <chart>`: Install a chart
- `helm upgrade <release> <chart>`: Upgrade a release
- `helm lint <chart>`: Check for issues

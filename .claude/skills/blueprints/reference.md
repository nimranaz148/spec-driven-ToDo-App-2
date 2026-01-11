# Blueprints Reference

## Spec-Driven Deployment Model

The deployment process follows the SDD-RI (Spec-Driven Development with Reusable Intelligence) model:
1. **Spec**: Define infrastructure requirements in markdown
2. **Plan**: Architecture the deployment strategy
3. **Tasks**: Break down into specific infrastructure tasks
4. **Implementation**: Generate manifests/charts using patterns

## Standard Patterns

### 1. Stateless Service Pattern
Designed for frontend and API services not holding persistent state.
- **Kind**: Deployment
- **Scaling**: HorizontalPodAutoscaler (HPA)
- **Service**: ClusterIP
- **Ingress**: Standard ingress rules

### 2. Stateful Service Pattern
Designed for databases and services requiring persistence.
- **Kind**: StatefulSet
- **Storage**: PersistentVolumeClaim (PVC)
- **Service**: Headless Service

### 3. Job Pattern
Designed for one-off tasks like migrations.
- **Kind**: Job
- **RestartPolicy**: OnFailure

### 4. CronJob Pattern
Designed for recurring tasks.
- **Kind**: CronJob

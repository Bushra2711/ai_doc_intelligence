# DocuMind AI — Kubernetes Deployment Layer

This directory contains the Kubernetes manifests for deploying the DocuMind AI application and its supporting services. It complements the existing Docker Compose setup and provides a version-controlled Kubernetes orchestration layer for the project.

## Architecture

The manifests cover the following components:

| Manifest | Component | Purpose |
|---|---|---|
| `namespace.yaml` | DocuMind namespace | Isolates project resources |
| `config.yaml` | Configuration | Non-secret application configuration and local demonstration values |
| `postgres.yaml` | PostgreSQL | Application database with persistent storage |
| `chroma.yaml` | ChromaDB | Vector-store service |
| `mlflow.yaml` | MLflow | Experiment/tracking service for MLOps |
| `backend.yaml` | DocuMind API | FastAPI backend deployment and service |
| `frontend.yaml` | DocuMind UI | Web frontend deployment and service |

The Kubernetes manifests follow the same major service boundaries as the project's Docker Compose environment.

**Docker Compose** remains the verified local development/integration path. **Kubernetes** is provided as the project's container orchestration/deployment configuration layer.

## Prerequisites

A Kubernetes environment with:

- Kubernetes cluster access
- `kubectl`
- Docker images for the backend and frontend
- Sufficient CPU, memory, and persistent storage for PostgreSQL and ChromaDB

For Docker Desktop Kubernetes, locally built images can be used with `imagePullPolicy: IfNotPresent`.

## Local Image Preparation

From the repository root:

    docker build -t documind-backend:latest ./backend
    docker build -t documind-frontend:latest ./frontend

Verify the images:

    docker images | findstr documind

## Deployment

Create/apply all project resources:

    kubectl apply -f k8s/

Check the resources:

    kubectl get namespace documind
    kubectl get deployments -n documind
    kubectl get pods -n documind
    kubectl get services -n documind

## Frontend Access

For local access through port forwarding:

    kubectl port-forward service/frontend 5173:80 -n documind

Then open:

    http://localhost:5173

## Runtime Verification

After deployment, verify rollout status:

    kubectl rollout status deployment/backend -n documind
    kubectl rollout status deployment/frontend -n documind

Then inspect:

    kubectl get pods -n documind
    kubectl get services -n documind

Application-specific health checks should also be performed through the exposed backend/API service.

## Current Local Verification Status

The Kubernetes manifests have been prepared and version-controlled in this repository.

**Runtime deployment status: not verified locally.**

During local validation, Docker Desktop Kubernetes initialization failed during cluster startup, so a successful `kubectl apply` / pod rollout could not be established. The manifests are therefore documented as deployment configuration evidence, not as proof of a running Kubernetes cluster.

This distinction is intentional so the repository does not claim a Kubernetes runtime deployment that was not successfully verified.

## Security and Production Considerations

These manifests are intended as a project-level deployment layer rather than a production cloud-cluster specification.

Before production use, review and configure:

- Kubernetes Secrets or an external secret manager for credentials and API keys
- Persistent storage classes and backup/restore procedures
- Ingress and TLS
- Resource requests and limits
- Horizontal Pod Autoscaling where appropriate
- Network policies
- RBAC/service accounts
- Container image registry and image versioning
- Managed PostgreSQL/ChromaDB alternatives where appropriate
- Observability, logging, and alerting
- Environment-specific configuration

Do not treat demonstration configuration values as production secrets.

## Cleanup

To remove the project resources:

    kubectl delete namespace documind

## Evidence Boundary

This directory provides:

- Kubernetes resource definitions
- Container deployment configuration
- Service boundaries for backend, frontend, PostgreSQL, ChromaDB, and MLflow
- Deployment and verification commands
- Documented local verification status and limitations

It does **not** by itself provide evidence of:

- a successfully running Kubernetes cluster
- production cloud deployment
- Azure-managed services
- production-grade autoscaling, ingress/TLS, backup, or disaster recovery

For the project's submission evidence, pair these manifests with the runtime/test evidence documented elsewhere in the repository.

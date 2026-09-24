# DocuMind Kubernetes Deployment

This directory provides a Kubernetes deployment layer alongside the existing Docker Compose setup.

## Architecture

- namespace.yaml — dedicated documind namespace
- config.yaml — non-secret configuration and local demonstration secrets
- postgres.yaml — PostgreSQL with persistent volume claim
- chroma.yaml — ChromaDB service
- mlflow.yaml — MLflow tracking service
- backend.yaml — DocuMind API
- frontend.yaml — DocuMind web UI

The manifests use the same service boundaries as docker-compose.yml. Docker Compose remains the local development/integration path; Kubernetes is the orchestration/deployment layer.

## Local image preparation

Build the application images from the repository root:

    docker build -t documind-backend:latest ./backend
    docker build -t documind-frontend:latest ./frontend

For Docker Desktop Kubernetes, the cluster can use locally built images with imagePullPolicy: IfNotPresent.

## Deploy

    kubectl apply -f k8s/
    kubectl get pods -n documind
    kubectl get services -n documind

For the frontend:

    kubectl port-forward service/frontend 5173:80 -n documind

Then open http://localhost:5173.

## Verify

    kubectl get deployments -n documind
    kubectl get pods -n documind
    kubectl get services -n documind
    kubectl rollout status deployment/backend -n documind
    kubectl rollout status deployment/frontend -n documind

## Cleanup

    kubectl delete namespace documind

## Scope and limitations

These manifests are intended as a project-level Kubernetes deployment layer, not a production cloud cluster specification. Persistent storage, secrets, ingress/TLS, autoscaling, resource quotas, and managed database services require environment-specific configuration before production use.

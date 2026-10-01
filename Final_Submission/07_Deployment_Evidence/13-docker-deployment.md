# Step 13 - Docker

The project provides production-style containers for backend and frontend plus PostgreSQL, ChromaDB and MLflow services.

Run:
```bash
docker compose up --build
```

Frontend: http://localhost:5173
Backend API: http://localhost:8000
Swagger: http://localhost:8000/docs
MLflow: http://localhost:5000
ChromaDB: http://localhost:8001

Database migrations should be applied with `docker compose exec backend alembic upgrade head`.

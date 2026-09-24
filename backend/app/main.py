from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    return {
        "service": settings.project_name,
        "status": "running",
    }

from fastapi.openapi.utils import get_openapi


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=settings.project_name,
        version=settings.project_version,
        description="DocuMind AI document intelligence API",
        routes=app.routes,
    )

    # Swagger UI can render a list[UploadFile] as array<string> without
    # exposing file pickers. Explicitly mark each batch item as binary.
    batch_schema = (
        schema.get("paths", {})
        .get("/api/v1/documents/batch-upload", {})
        .get("post", {})
        .get("requestBody", {})
        .get("content", {})
        .get("multipart/form-data", {})
        .get("schema", {})
    )
    if isinstance(batch_schema, dict):
        properties = batch_schema.setdefault("properties", {})
        properties["files"] = {
            "type": "array",
            "items": {"type": "string", "format": "binary"},
            "description": "Multiple supported documents",
        }

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

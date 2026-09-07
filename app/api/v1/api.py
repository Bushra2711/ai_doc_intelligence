from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.documents import router as documents_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.users import router as users_router

api_router = APIRouter()

# Health APIs
api_router.include_router(
    health_router,
    prefix="/health",
    tags=["health"],
)

# Authentication APIs
api_router.include_router(
    auth_router,
)

# User APIs
api_router.include_router(users_router)

# Document APIs
api_router.include_router(documents_router)
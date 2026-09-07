from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter()


@router.get("")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
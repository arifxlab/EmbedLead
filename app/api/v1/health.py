from fastapi import APIRouter
from sqlalchemy import text

from app.core.redis import redis_client
from app.db.session import async_session_factory

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
    }


@router.get("/ready")
async def readiness() -> dict[str, str]:
    async with async_session_factory() as session:
        await session.execute(text("SELECT 1"))

    await redis_client.ping()

    return {
        "status": "ready",
        "database": "ok",
        "redis": "ok",
    }

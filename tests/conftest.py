from collections.abc import AsyncGenerator

import httpx
import pytest
from app.core.redis import close_redis
from app.db.session import close_database
from app.main import app


@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    app.state.http_client = httpx.AsyncClient()

    transport = httpx.ASGITransport(app=app)

    try:
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            yield client
    finally:
        await app.state.http_client.aclose()
        await close_database()
        await close_redis()

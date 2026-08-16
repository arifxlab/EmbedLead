import uuid

import pytest
from app.core.limiter import limiter
from app.db.session import async_session_factory
from app.models.tenant import Tenant
from app.models.widget import Widget
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_public_lead_submission(client: AsyncClient) -> None:
    tenant = Tenant(
        name="Integration Test Tenant",
        slug=f"integration-test-{uuid.uuid4().hex[:12]}",
    )

    async with async_session_factory() as session:
        session.add(tenant)
        await session.flush()

        widget = Widget(
            tenant_id=tenant.id,
            name="Integration Test Widget",
            public_key=f"pk_test_{uuid.uuid4().hex[:20]}",
            is_active=True,
        )

        session.add(widget)
        await session.commit()
        await session.refresh(widget)

        public_key = widget.public_key

    response = await client.post(
        f"/api/v1/public/widgets/{public_key}/leads",
        json={
            "name": "Integration Test Lead",
            "email": "integration@example.com",
            "message": "Testing the public lead submission API.",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert uuid.UUID(data["id"])
    assert data["message"] == "Lead submitted successfully"


@pytest.mark.asyncio
async def test_public_lead_rejects_unknown_widget(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/public/widgets/pk_nonexistent_widget/leads",
        json={
            "name": "Unknown Widget Test",
            "email": "unknown@example.com",
            "message": "This should be rejected.",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Widget not found"


@pytest.mark.asyncio
async def test_public_lead_rejects_inactive_widget(client: AsyncClient) -> None:
    tenant = Tenant(
        name="Inactive Widget Test Tenant",
        slug=f"inactive-widget-{uuid.uuid4().hex[:12]}",
    )

    async with async_session_factory() as session:
        session.add(tenant)
        await session.flush()

        widget = Widget(
            tenant_id=tenant.id,
            name="Inactive Test Widget",
            public_key=f"pk_inactive_{uuid.uuid4().hex[:20]}",
            is_active=False,
        )

        session.add(widget)
        await session.commit()
        await session.refresh(widget)

        public_key = widget.public_key

    response = await client.post(
        f"/api/v1/public/widgets/{public_key}/leads",
        json={
            "name": "Inactive Widget Test",
            "email": "inactive@example.com",
            "message": "This should be rejected.",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Widget is inactive"


@pytest.mark.asyncio
async def test_public_lead_rejects_invalid_email(client: AsyncClient) -> None:
    tenant = Tenant(
        name="Invalid Email Test Tenant",
        slug=f"invalid-email-{uuid.uuid4().hex[:12]}",
    )

    async with async_session_factory() as session:
        session.add(tenant)
        await session.flush()

        widget = Widget(
            tenant_id=tenant.id,
            name="Invalid Email Test Widget",
            public_key=f"pk_email_{uuid.uuid4().hex[:20]}",
            is_active=True,
        )

        session.add(widget)
        await session.commit()
        await session.refresh(widget)

        public_key = widget.public_key

    response = await client.post(
        f"/api/v1/public/widgets/{public_key}/leads",
        json={
            "name": "Invalid Email Test",
            "email": "not-an-email",
            "message": "This request should fail validation.",
        },
    )

    assert response.status_code == 422

    data = response.json()
    assert data["detail"]


@pytest.mark.asyncio
async def test_public_lead_rejects_oversized_payload(client: AsyncClient) -> None:
    oversized_message = "x" * 20_000

    response = await client.post(
        "/api/v1/public/widgets/pk_nonexistent_widget/leads",
        json={
            "name": "Oversized Payload Test",
            "email": "oversized@example.com",
            "message": oversized_message,
        },
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Request payload too large"


@pytest.mark.asyncio
async def test_public_lead_rate_limit(client: AsyncClient) -> None:
    limiter.reset()

    try:
        for _ in range(60):
            response = await client.post(
                "/api/v1/public/widgets/pk_nonexistent_widget/leads",
                json={
                    "name": "Rate Limit Test",
                    "email": "rate-limit@example.com",
                    "message": "Testing the public API rate limiter.",
                },
            )

            assert response.status_code == 404
            assert response.json()["detail"] == "Widget not found"

        response = await client.post(
            "/api/v1/public/widgets/pk_nonexistent_widget/leads",
            json={
                "name": "Rate Limit Test",
                "email": "rate-limit@example.com",
                "message": "This request should be rate limited.",
            },
        )

        assert response.status_code == 429
    finally:
        limiter.reset()


@pytest.mark.asyncio
async def test_get_lead_rejects_unknown_lead(client: AsyncClient) -> None:
    missing_lead_id = uuid.uuid4()

    response = await client.get(
        f"/api/v1/leads/{missing_lead_id}",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Lead not found"

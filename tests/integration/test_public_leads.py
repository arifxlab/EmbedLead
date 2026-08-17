import uuid

import pytest
from app.core.limiter import limiter
from app.core.redis import delete_cached, get_cached
from app.db.session import async_session_factory
from app.models.lead import Lead
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
async def test_public_widget_config_is_cached_and_tenant_safe(
    client: AsyncClient,
) -> None:
    tenant = Tenant(
        name="Public Config Tenant",
        slug=f"public-config-{uuid.uuid4().hex[:12]}",
    )

    async with async_session_factory() as session:
        session.add(tenant)
        await session.flush()

        widget = Widget(
            tenant_id=tenant.id,
            name="Cached Widget",
            public_key=f"pk_test_{uuid.uuid4().hex[:20]}",
            is_active=True,
        )

        session.add(widget)
        await session.commit()
        await session.refresh(widget)

        public_key = widget.public_key
        widget_id = widget.id

    cache_key = f"widget:public-config:{public_key}"

    await delete_cached(cache_key)

    # First request: cache miss -> database -> Redis.
    first_response = await client.get(
        f"/api/v1/public/widgets/{public_key}/config",
    )

    assert first_response.status_code == 200

    first_data = first_response.json()

    assert first_data["id"] == str(widget_id)
    assert first_data["name"] == "Cached Widget"
    assert first_data["public_key"] == public_key
    assert first_data["is_active"] is True
    assert "tenant_id" not in first_data

    assert first_response.headers["cache-control"] == "public, max-age=300"

    cached_value = await get_cached(cache_key)

    assert cached_value is not None

    # Verify the cached value has the expected Redis TTL.
    from app.core.redis import redis_client

    ttl = await redis_client.ttl(cache_key)

    assert 0 < ttl <= 300

    # Change the database directly. The cached response must remain unchanged.
    async with async_session_factory() as session:
        stored_widget = await session.get(Widget, widget_id)

        assert stored_widget is not None

        stored_widget.name = "Changed In Database"

        await session.commit()

    second_response = await client.get(
        f"/api/v1/public/widgets/{public_key}/config",
    )

    assert second_response.status_code == 200

    second_data = second_response.json()

    assert second_data["name"] == "Cached Widget"
    assert second_data["name"] != "Changed In Database"


@pytest.mark.asyncio
async def test_get_lead_requires_authentication(client: AsyncClient) -> None:
    missing_lead_id = uuid.uuid4()

    response = await client.get(
        f"/api/v1/leads/{missing_lead_id}",
    )

    assert response.status_code == 401


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
async def test_tenant_isolation_for_widgets(client: AsyncClient) -> None:
    tenant_a = Tenant(
        name="Tenant A",
        slug=f"tenant-a-{uuid.uuid4().hex[:12]}",
    )

    tenant_b = Tenant(
        name="Tenant B",
        slug=f"tenant-b-{uuid.uuid4().hex[:12]}",
    )

    async with async_session_factory() as session:
        session.add_all([tenant_a, tenant_b])
        await session.flush()

        tenant_a_id = tenant_a.id
        tenant_b_id = tenant_b.id

        await session.commit()

    password = "StrongPassword123!"

    register_a = await client.post(
        "/api/v1/auth/register",
        json={
            "tenant_id": str(tenant_a_id),
            "email": f"user-a-{uuid.uuid4().hex[:12]}@example.com",
            "password": password,
        },
    )

    assert register_a.status_code == 201

    user_a_email = register_a.json()["email"]

    register_b = await client.post(
        "/api/v1/auth/register",
        json={
            "tenant_id": str(tenant_b_id),
            "email": f"user-b-{uuid.uuid4().hex[:12]}@example.com",
            "password": password,
        },
    )

    assert register_b.status_code == 201

    user_b_email = register_b.json()["email"]

    login_a = await client.post(
        "/api/v1/auth/login",
        json={
            "email": user_a_email,
            "password": password,
        },
    )

    assert login_a.status_code == 200

    token_a = login_a.json()["access_token"]

    login_b = await client.post(
        "/api/v1/auth/login",
        json={
            "email": user_b_email,
            "password": password,
        },
    )

    assert login_b.status_code == 200

    token_b = login_b.json()["access_token"]

    create_widget = await client.post(
        "/api/v1/widgets",
        headers={
            "Authorization": f"Bearer {token_a}",
        },
        json={
            "name": "Tenant A Widget",
        },
    )

    assert create_widget.status_code == 201

    widget_id = create_widget.json()["id"]

    same_tenant_response = await client.get(
        f"/api/v1/widgets/{widget_id}",
        headers={
            "Authorization": f"Bearer {token_a}",
        },
    )

    assert same_tenant_response.status_code == 200
    assert same_tenant_response.json()["id"] == widget_id

    cross_tenant_response = await client.get(
        f"/api/v1/widgets/{widget_id}",
        headers={
            "Authorization": f"Bearer {token_b}",
        },
    )

    assert cross_tenant_response.status_code == 404
    assert cross_tenant_response.json()["detail"] == "Widget not found"


@pytest.mark.asyncio
async def test_created_widget_public_key_accepts_lead(
    client: AsyncClient,
) -> None:
    tenant = Tenant(
        name="Generated Key Test Tenant",
        slug=f"generated-key-{uuid.uuid4().hex[:12]}",
    )

    async with async_session_factory() as session:
        session.add(tenant)
        await session.flush()

        tenant_id = tenant.id

        await session.commit()

    password = "StrongPassword123!"
    email = f"generated-key-{uuid.uuid4().hex[:12]}@example.com"

    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "tenant_id": str(tenant_id),
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    create_widget_response = await client.post(
        "/api/v1/widgets",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": "Generated Key Test Widget",
        },
    )

    assert create_widget_response.status_code == 201

    widget_data = create_widget_response.json()

    assert widget_data["name"] == "Generated Key Test Widget"
    assert widget_data["tenant_id"] == str(tenant_id)
    assert widget_data["public_key"].startswith("pk_live_")

    public_key = widget_data["public_key"]

    lead_response = await client.post(
        f"/api/v1/public/widgets/{public_key}/leads",
        json={
            "name": "Generated Key Lead",
            "email": "generated-key-lead@example.com",
            "message": "Testing the generated widget public key.",
        },
    )

    assert lead_response.status_code == 201

    lead_data = lead_response.json()

    assert "id" in lead_data
    assert uuid.UUID(lead_data["id"])
    assert lead_data["message"] == "Lead submitted successfully"


@pytest.mark.asyncio
async def test_lead_listing_pagination_and_tenant_isolation(
    client: AsyncClient,
) -> None:
    tenant_a = Tenant(
        name="Lead Listing Tenant A",
        slug=f"lead-list-a-{uuid.uuid4().hex[:12]}",
    )

    tenant_b = Tenant(
        name="Lead Listing Tenant B",
        slug=f"lead-list-b-{uuid.uuid4().hex[:12]}",
    )

    async with async_session_factory() as session:
        session.add_all([tenant_a, tenant_b])
        await session.flush()

        widget_a = Widget(
            tenant_id=tenant_a.id,
            name="Tenant A Widget",
            public_key=f"pk_test_{uuid.uuid4().hex[:20]}",
            is_active=True,
        )

        widget_b = Widget(
            tenant_id=tenant_b.id,
            name="Tenant B Widget",
            public_key=f"pk_test_{uuid.uuid4().hex[:20]}",
            is_active=True,
        )

        session.add_all([widget_a, widget_b])
        await session.flush()

        for index in range(5):
            session.add(
                Lead(
                    tenant_id=tenant_a.id,
                    widget_id=widget_a.id,
                    name=f"Tenant A Lead {index}",
                    email=f"tenant-a-{index}-{uuid.uuid4().hex[:8]}@example.com",
                    message=f"Tenant A message {index}",
                )
            )

        for index in range(2):
            session.add(
                Lead(
                    tenant_id=tenant_b.id,
                    widget_id=widget_b.id,
                    name=f"Tenant B Lead {index}",
                    email=f"tenant-b-{index}-{uuid.uuid4().hex[:8]}@example.com",
                    message=f"Tenant B message {index}",
                )
            )

        await session.commit()

        tenant_a_id = tenant_a.id
        tenant_b_id = tenant_b.id

    password = "StrongPassword123!"

    email_a = f"listing-a-{uuid.uuid4().hex[:12]}@example.com"
    email_b = f"listing-b-{uuid.uuid4().hex[:12]}@example.com"

    register_a = await client.post(
        "/api/v1/auth/register",
        json={
            "tenant_id": str(tenant_a_id),
            "email": email_a,
            "password": password,
        },
    )

    register_b = await client.post(
        "/api/v1/auth/register",
        json={
            "tenant_id": str(tenant_b_id),
            "email": email_b,
            "password": password,
        },
    )

    assert register_a.status_code == 201
    assert register_b.status_code == 201

    login_a = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email_a,
            "password": password,
        },
    )

    login_b = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email_b,
            "password": password,
        },
    )

    assert login_a.status_code == 200
    assert login_b.status_code == 200

    token_a = login_a.json()["access_token"]
    token_b = login_b.json()["access_token"]

    unauthenticated = await client.get("/api/v1/leads")

    assert unauthenticated.status_code == 401

    page_one = await client.get(
        "/api/v1/leads",
        headers={
            "Authorization": f"Bearer {token_a}",
        },
        params={
            "page": 1,
            "page_size": 2,
        },
    )

    assert page_one.status_code == 200

    page_one_data = page_one.json()

    assert page_one_data["page"] == 1
    assert page_one_data["page_size"] == 2
    assert page_one_data["total"] == 5
    assert page_one_data["pages"] == 3
    assert len(page_one_data["items"]) == 2

    page_one_ids = [item["id"] for item in page_one_data["items"]]
    assert len(set(page_one_ids)) == 2
    assert all(item["name"].startswith("Tenant A Lead") for item in page_one_data["items"])

    page_two = await client.get(
        "/api/v1/leads",
        headers={
            "Authorization": f"Bearer {token_a}",
        },
        params={
            "page": 2,
            "page_size": 2,
        },
    )

    assert page_two.status_code == 200

    page_two_data = page_two.json()

    assert page_two_data["page"] == 2
    assert page_two_data["page_size"] == 2
    assert page_two_data["total"] == 5
    assert page_two_data["pages"] == 3
    assert len(page_two_data["items"]) == 2

    page_three = await client.get(
        "/api/v1/leads",
        headers={
            "Authorization": f"Bearer {token_a}",
        },
        params={
            "page": 3,
            "page_size": 2,
        },
    )

    assert page_three.status_code == 200

    page_three_data = page_three.json()

    assert page_three_data["page"] == 3
    assert page_three_data["page_size"] == 2
    assert page_three_data["total"] == 5
    assert page_three_data["pages"] == 3
    assert len(page_three_data["items"]) == 1

    tenant_b_response = await client.get(
        "/api/v1/leads",
        headers={
            "Authorization": f"Bearer {token_b}",
        },
    )

    assert tenant_b_response.status_code == 200

    tenant_b_data = tenant_b_response.json()

    assert tenant_b_data["total"] == 2
    assert tenant_b_data["pages"] == 1
    assert len(tenant_b_data["items"]) == 2

    assert all(item["name"].startswith("Tenant B") for item in tenant_b_data["items"])

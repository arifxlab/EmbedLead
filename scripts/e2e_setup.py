import asyncio
import uuid

from app.db.session import async_session_factory
from app.models.tenant import Tenant
from app.models.widget import Widget


async def main() -> None:
    tenant = Tenant(
        name="E2E Test Tenant",
        slug=f"e2e-{uuid.uuid4().hex[:12]}",
    )

    async with async_session_factory() as session:
        session.add(tenant)
        await session.flush()

        widget = Widget(
            tenant_id=tenant.id,
            name="E2E Test Widget",
            public_key=f"pk_e2e_{uuid.uuid4().hex[:20]}",
            is_active=True,
        )

        session.add(widget)
        await session.commit()
        await session.refresh(widget)

        print(f"PUBLIC_KEY={widget.public_key}")
        print(f"WIDGET_ID={widget.id}")


if __name__ == "__main__":
    asyncio.run(main())

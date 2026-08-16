import asyncio
import uuid

from app.db.session import async_session_factory
from app.models.tenant import Tenant


async def main() -> None:
    async with async_session_factory() as session:
        tenant = Tenant(
            name="EmbedLead Demo",
            slug=f"embedlead-demo-{uuid.uuid4().hex[:8]}",
        )

        session.add(tenant)
        await session.commit()
        await session.refresh(tenant)

        print(f"TENANT_ID: {tenant.id}")
        print(f"TENANT_NAME: {tenant.name}")
        print(f"TENANT_SLUG: {tenant.slug}")


if __name__ == "__main__":
    asyncio.run(main())

import asyncio

from app.db.session import async_session_factory
from app.services.lead import LeadService

TENANT_ID = "b5ff829c-c344-45d4-b8de-9769e40a0678"
WIDGET_ID = "64a6ed82-0a7d-4304-87c9-fd018fb0be39"


async def main() -> None:
    async with async_session_factory() as session:
        service = LeadService(session)

        lead = await service.create_lead(
            tenant_id=__import__("uuid").UUID(TENANT_ID),
            widget_id=__import__("uuid").UUID(WIDGET_ID),
            name="EmbedLead Demo",
            email="demo@example.com",
            message="First real lead created through the service layer.",
        )

        print(f"Lead ID: {lead.id}")
        print(f"Tenant ID: {lead.tenant_id}")
        print(f"Widget ID: {lead.widget_id}")
        print(f"Email: {lead.email}")
        print(f"Created At: {lead.created_at}")


if __name__ == "__main__":
    asyncio.run(main())

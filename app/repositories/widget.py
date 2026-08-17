from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.widget import Widget


class WidgetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        tenant_id: UUID,
        name: str,
        public_key: str,
    ) -> Widget:
        widget = Widget(
            tenant_id=tenant_id,
            name=name,
            public_key=public_key,
        )

        self.session.add(widget)
        await self.session.flush()

        return widget

    async def get_by_id(
        self,
        widget_id: UUID,
        tenant_id: UUID,
    ) -> Widget | None:
        result = await self.session.execute(
            select(Widget).where(
                Widget.id == widget_id,
                Widget.tenant_id == tenant_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_public_key(
        self,
        public_key: str,
    ) -> Widget | None:
        result = await self.session.execute(select(Widget).where(Widget.public_key == public_key))

        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: UUID,
    ) -> list[Widget]:
        result = await self.session.execute(
            select(Widget).where(Widget.tenant_id == tenant_id).order_by(Widget.created_at.desc())
        )

        return list(result.scalars().all())

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.widget import Widget
from app.repositories.widget import WidgetRepository


class WidgetService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session
        self.repository = WidgetRepository(session)

    async def create_widget(
        self,
        tenant_id: UUID,
        name: str,
        public_key: str,
    ) -> Widget:
        widget = await self.repository.create(
            tenant_id=tenant_id,
            name=name,
            public_key=public_key,
        )

        await self.session.commit()
        await self.session.refresh(widget)

        return widget

    async def get_widget(
        self,
        widget_id: UUID,
    ) -> Widget:
        widget = await self.repository.get_by_id(widget_id)

        if widget is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found",
            )

        return widget

    async def get_public_widget(
        self,
        public_key: str,
    ) -> Widget:
        widget = await self.repository.get_by_public_key(public_key)

        if widget is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found",
            )

        if not widget.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Widget is inactive",
            )

        return widget

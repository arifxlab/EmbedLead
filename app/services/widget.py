import json
import secrets
from typing import cast
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import WidgetInactiveError, WidgetNotFoundError
from app.core.redis import delete_cached, get_cached, set_cached
from app.models.widget import Widget
from app.repositories.widget import WidgetRepository

PUBLIC_KEY_PREFIX = "pk_live_"
PUBLIC_WIDGET_CACHE_PREFIX = "widget:public-config:"

PublicWidgetConfigData = dict[str, str | bool]


class WidgetService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session
        self.repository = WidgetRepository(session)
        self.settings = get_settings()

    async def create_widget(
        self,
        tenant_id: UUID,
        name: str,
    ) -> Widget:
        public_key = f"{PUBLIC_KEY_PREFIX}{secrets.token_urlsafe(32)}"

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
        tenant_id: UUID,
    ) -> Widget:
        widget = await self.repository.get_by_id(
            widget_id=widget_id,
            tenant_id=tenant_id,
        )

        if widget is None:
            raise WidgetNotFoundError

        return widget

    async def update_widget(
        self,
        widget_id: UUID,
        tenant_id: UUID,
        name: str | None = None,
        is_active: bool | None = None,
    ) -> Widget:
        widget = await self.get_widget(
            widget_id=widget_id,
            tenant_id=tenant_id,
        )

        await self.repository.update(
            widget=widget,
            name=name,
            is_active=is_active,
        )

        await self.session.commit()
        await self.session.refresh(widget)

        await self.invalidate_public_widget_config(
            public_key=widget.public_key,
        )

        return widget

    async def delete_widget(
        self,
        widget_id: UUID,
        tenant_id: UUID,
    ) -> None:
        widget = await self.get_widget(
            widget_id=widget_id,
            tenant_id=tenant_id,
        )

        public_key = widget.public_key

        await self.repository.delete(widget)

        await self.session.commit()

        await self.invalidate_public_widget_config(
            public_key=public_key,
        )

    async def get_public_widget(
        self,
        public_key: str,
    ) -> Widget:
        widget = await self.repository.get_by_public_key(public_key)

        if widget is None:
            raise WidgetNotFoundError

        if not widget.is_active:
            raise WidgetInactiveError

        return widget

    async def get_public_widget_config(
        self,
        public_key: str,
    ) -> PublicWidgetConfigData:
        cache_key = f"{PUBLIC_WIDGET_CACHE_PREFIX}{public_key}"

        cached = await get_cached(cache_key)

        if cached is not None:
            cached_config = json.loads(cached)

            if not isinstance(cached_config, dict):
                raise ValueError("Cached widget configuration is invalid")

            return cast(PublicWidgetConfigData, cached_config)

        widget = await self.get_public_widget(public_key)

        config: PublicWidgetConfigData = {
            "id": str(widget.id),
            "name": widget.name,
            "public_key": widget.public_key,
            "is_active": widget.is_active,
        }

        await set_cached(
            key=cache_key,
            value=json.dumps(config),
            ttl_seconds=self.settings.widget_cache_ttl_seconds,
        )

        return config

    async def invalidate_public_widget_config(
        self,
        public_key: str,
    ) -> None:
        cache_key = f"{PUBLIC_WIDGET_CACHE_PREFIX}{public_key}"

        await delete_cached(cache_key)

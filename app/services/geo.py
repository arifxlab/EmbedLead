from dataclasses import dataclass

import httpx

from app.core.config import get_settings

settings = get_settings()


@dataclass(frozen=True)
class GeoMetadata:
    ip_address: str
    country: str | None = None
    region: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class GeoService:
    def __init__(
        self,
        client: httpx.AsyncClient,
    ) -> None:
        self.client = client

    async def lookup(
        self,
        ip_address: str,
    ) -> GeoMetadata:
        try:
            return await self._lookup_primary(ip_address)
        except (httpx.HTTPError, ValueError):
            return await self._lookup_fallback(ip_address)

    async def _lookup_primary(
        self,
        ip_address: str,
    ) -> GeoMetadata:
        response = await self.client.get(
            f"{settings.geo_primary_url}/{ip_address}/json/",
            timeout=5.0,
        )
        response.raise_for_status()

        data = response.json()

        if data.get("error"):
            raise ValueError("Primary geolocation provider returned an error")

        return GeoMetadata(
            ip_address=ip_address,
            country=data.get("country_name"),
            region=data.get("region"),
            city=data.get("city"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
        )

    async def _lookup_fallback(
        self,
        ip_address: str,
    ) -> GeoMetadata:
        response = await self.client.get(
            f"{settings.geo_fallback_url}/{ip_address}",
            timeout=5.0,
        )
        response.raise_for_status()

        data = response.json()

        if data.get("success") is False:
            raise ValueError("Fallback geolocation provider returned an error")

        return GeoMetadata(
            ip_address=ip_address,
            country=data.get("country"),
            region=data.get("region"),
            city=data.get("city"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
        )

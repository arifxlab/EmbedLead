import httpx
import pytest
from app.services.geo import GeoService


@pytest.mark.asyncio
async def test_geo_lookup_uses_primary_provider() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == ("https://ipapi.co/8.8.8.8/json/")

        return httpx.Response(
            200,
            json={
                "country_name": "United States",
                "region": "California",
                "city": "Mountain View",
                "latitude": 37.386,
                "longitude": -122.0838,
            },
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as client:
        service = GeoService(client)

        result = await service.lookup("8.8.8.8")

    assert result.ip_address == "8.8.8.8"
    assert result.country == "United States"
    assert result.region == "California"
    assert result.city == "Mountain View"
    assert result.latitude == 37.386
    assert result.longitude == -122.0838


@pytest.mark.asyncio
async def test_geo_lookup_falls_back_when_primary_fails() -> None:
    requested_urls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested_urls.append(str(request.url))

        if "ipapi.co" in str(request.url):
            return httpx.Response(
                503,
                request=request,
            )

        return httpx.Response(
            200,
            json={
                "success": True,
                "country": "United States",
                "region": "California",
                "city": "Mountain View",
                "latitude": 37.386,
                "longitude": -122.0838,
            },
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(transport=transport) as client:
        service = GeoService(client)

        result = await service.lookup("8.8.8.8")

    assert requested_urls == [
        "https://ipapi.co/8.8.8.8/json/",
        "https://ipwho.is/8.8.8.8",
    ]

    assert result.ip_address == "8.8.8.8"
    assert result.country == "United States"
    assert result.region == "California"
    assert result.city == "Mountain View"
    assert result.latitude == 37.386
    assert result.longitude == -122.0838

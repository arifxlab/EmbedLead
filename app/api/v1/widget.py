from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter(
    tags=["widget"],
)

WIDGET_DIR = Path(__file__).resolve().parents[2] / "widget"


def _serve_widget(version: str) -> PlainTextResponse:
    widget_path = WIDGET_DIR / f"widget.{version}.js"
    widget_js = widget_path.read_text(encoding="utf-8")

    return PlainTextResponse(
        content=widget_js,
        media_type="application/javascript",
        headers={
            "Cache-Control": "public, max-age=31536000, immutable",
        },
    )


@router.get(
    "/widget.v1.js",
    response_class=PlainTextResponse,
    include_in_schema=False,
)
async def get_widget_script_v1() -> PlainTextResponse:
    return _serve_widget("v1")

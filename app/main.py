from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import cast

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import (
    InvalidCredentialsError,
    LeadNotFoundError,
    UserAlreadyExistsError,
    WidgetInactiveError,
    WidgetNotFoundError,
)
from app.core.limiter import limiter
from app.core.redis import close_redis
from app.db.session import close_database

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    yield

    await close_database()
    await close_redis()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Multi-tenant embeddable lead-capture infrastructure with secure public submission APIs."
    ),
    lifespan=lifespan,
)

app.state.limiter = limiter

rate_limit_handler = cast(
    Callable[[Request, Exception], Response],
    _rate_limit_exceeded_handler,
)

app.add_exception_handler(
    RateLimitExceeded,
    rate_limit_handler,
)


@app.exception_handler(WidgetNotFoundError)
async def handle_widget_not_found(
    _: Request,
    __: WidgetNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": "Widget not found"},
    )


@app.exception_handler(WidgetInactiveError)
async def handle_widget_inactive(
    _: Request,
    __: WidgetInactiveError,
) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={"detail": "Widget is inactive"},
    )


@app.exception_handler(LeadNotFoundError)
async def handle_lead_not_found(
    _: Request,
    __: LeadNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": "Lead not found"},
    )


@app.exception_handler(UserAlreadyExistsError)
async def handle_user_already_exists(
    _: Request,
    __: UserAlreadyExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": "User already exists"},
    )


@app.exception_handler(InvalidCredentialsError)
async def handle_invalid_credentials(
    _: Request,
    __: InvalidCredentialsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": "Invalid credentials"},
    )


@app.middleware("http")
async def enforce_payload_size(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    body = await request.body()

    if len(body) > settings.max_submission_payload_bytes:
        return JSONResponse(
            status_code=413,
            content={"detail": "Request payload too large"},
        )

    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(
    api_router,
    prefix=settings.api_prefix,
)

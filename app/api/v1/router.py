from fastapi import APIRouter

from app.api.v1.analytics import router as analytics_router
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.leads import router as leads_router
from app.api.v1.public import router as public_router
from app.api.v1.widget import router as widget_router
from app.api.v1.widgets import router as widgets_router

api_router = APIRouter()

api_router.include_router(analytics_router)
api_router.include_router(auth_router)
api_router.include_router(health_router)
api_router.include_router(widgets_router)
api_router.include_router(leads_router)
api_router.include_router(public_router)
api_router.include_router(widget_router)

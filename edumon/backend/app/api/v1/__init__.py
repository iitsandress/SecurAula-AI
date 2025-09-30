"""
API v1 routes
"""
from fastapi import APIRouter
from .auth import router as auth_router
from .clients import router as clients_router
from .sessions import router as sessions_router
from .metrics import router as metrics_router
from .dashboard import router as dashboard_router
from .admin import router as admin_router

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(clients_router, prefix="/clients", tags=["clients"])
api_router.include_router(sessions_router, prefix="/sessions", tags=["sessions"])
api_router.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])

__all__ = ["api_router"]
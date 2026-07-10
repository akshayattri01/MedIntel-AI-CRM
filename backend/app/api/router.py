from fastapi import APIRouter
from app.api.routes import ai, analytics, auth, dashboard, followups, hcp, history, interactions, tools, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(hcp.router, prefix="/hcp", tags=["hcp"])
api_router.include_router(interactions.router, prefix="/interactions", tags=["interactions"])
api_router.include_router(followups.router, prefix="/follow-ups", tags=["follow-ups"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])

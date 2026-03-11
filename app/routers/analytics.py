from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, get_current_active_user
from app.models.usuario import Usuario
from app.services.analytics import AnalyticsService, DashboardResponse

router = APIRouter()

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard_principal(
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    return await AnalyticsService.get_dashboard_mensual(db, current_user)

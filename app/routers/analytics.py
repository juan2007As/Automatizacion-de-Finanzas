from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.services.analytics_service import AnalyticsService, DashboardResponse

router = APIRouter()

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Dashboard Financiero Mensual",
    description="Ejecuta la máquina analítica. Cruza el onboarding base con los gastos/ahorros en la moneda principal y calcula banderas de riesgo (Fuga de capital)."
)
async def obtener_dashboard(
    db: AsyncSession = Depends(get_db_session)
) -> DashboardResponse:
    return await AnalyticsService.get_dashboard_mensual(db)

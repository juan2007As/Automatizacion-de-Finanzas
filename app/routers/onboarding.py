from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.onboarding import OnboardingBasico
from app.services.onboarding_service import OnboardingService

router = APIRouter()

@router.post(
    "/",
    response_model=OnboardingBasico,
    status_code=status.HTTP_201_CREATED,
    summary="Completar Onboarding",
    description="Declara la moneda base, ingreso fijo y saldo actual. Este es el Punto Cero del motor analítico."
)
async def crear_onboarding(
    payload: OnboardingBasico,
    db: AsyncSession = Depends(get_db_session)
):
    return await OnboardingService.registrar_punto_cero(db, payload)

@router.get(
    "/",
    response_model=OnboardingBasico,
    summary="Ver Onboarding",
)
async def ver_onboarding(
    db: AsyncSession = Depends(get_db_session)
):
    perfil = await OnboardingService.obtener_perfil_activo(db)
    if not perfil:
        return {} # El frontend debe mostrar la pantalla de registro si viene vacío
    return perfil

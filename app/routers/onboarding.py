from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from decimal import Decimal
from app.api.deps import get_current_active_user, get_db_session
from app.models.usuario import Usuario
from app.models.onboarding import OnboardingInfo
from app.schemas.onboarding import OnboardingBasico

router = APIRouter()

@router.post("/", response_model=OnboardingBasico, status_code=status.HTTP_201_CREATED)
async def setup_onboarding(
    onboarding_data: OnboardingBasico,
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    stmt_check = select(OnboardingInfo).limit(1)
    if (await db.execute(stmt_check)).scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Onboarding ya completado.")

    ingreso_centavos = int(onboarding_data.ingreso_mensual_promedio * Decimal("100"))
    saldo_centavos = int(onboarding_data.saldo_actual * Decimal("100"))

    nuevo_perfil = OnboardingInfo(
        moneda_principal=onboarding_data.moneda_principal,
        ingreso_mensual_promedio_centavos=ingreso_centavos,
        saldo_actual_centavos=saldo_centavos,
        meta_principal=onboarding_data.meta_principal
    )
    db.add(nuevo_perfil)

    stmt_user = select(Usuario).where(Usuario.id == current_user.id)
    user_to_update = (await db.execute(stmt_user)).scalar_one()
    user_to_update.onboarding_completed = True

    await db.commit()

    return onboarding_data

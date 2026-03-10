from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_tenant_db, get_current_active_user, get_db_session
from app.models.usuario import Usuario
from app.models.onboarding import OnboardingInfo
from app.schemas.onboarding import OnboardingBasico

router = APIRouter()

@router.post("/", response_model=OnboardingBasico, status_code=status.HTTP_201_CREATED)
async def setup_onboarding(
    onboarding_data: OnboardingBasico,
    current_user: Usuario = Depends(get_current_active_user),
    db_tenant: AsyncSession = Depends(get_current_tenant_db),
    db_public: AsyncSession = Depends(get_db_session)
):
    stmt_check = select(OnboardingInfo).limit(1)
    if (await db_tenant.execute(stmt_check)).scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Onboarding ya completado.")

    nuevo_perfil = OnboardingInfo(**onboarding_data.model_dump())
    db_tenant.add(nuevo_perfil)
    await db_tenant.commit()

    stmt_user = select(Usuario).where(Usuario.id == current_user.id)
    user_to_update = (await db_public.execute(stmt_user)).scalar_one()
    user_to_update.onboarding_completed = True
    await db_public.commit()

    return onboarding_data

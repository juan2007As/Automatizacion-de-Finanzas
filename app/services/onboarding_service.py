from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.schemas.onboarding import OnboardingBasico
from app.schemas.moneda_utils import decimal_a_unidad_menor, unidad_menor_a_decimal
from app.repositories.onboarding_repo import onboarding_repo
from app.core.logger import logger

class OnboardingService:
    @staticmethod
    async def registrar_punto_cero(db: AsyncSession, payload_onboarding: OnboardingBasico) -> OnboardingBasico:
        existentes = await onboarding_repo.get_multi(db, limit=1)
        if existentes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El Onboarding ya fue completado previamente."
            )

        moneda = payload_onboarding.moneda_principal
        ingreso_sqlite = decimal_a_unidad_menor(payload_onboarding.ingreso_mensual_promedio, moneda)
        saldo_sqlite = decimal_a_unidad_menor(payload_onboarding.saldo_actual, moneda)

        obj_in = {
            "moneda_principal": moneda,
            "ingreso_mensual_promedio_unidad_menor": ingreso_sqlite,
            "saldo_actual_unidad_menor": saldo_sqlite,
            "meta_principal": payload_onboarding.meta_principal
        }

        try:
            await onboarding_repo.create(db, obj_in=obj_in)
            await db.commit()
            logger.info(f"Onboarding completado. Moneda base: {moneda}")
            return payload_onboarding
        except Exception:
            await db.rollback()
            logger.error("Error crítico guardando Onboarding", exc_info=True)
            raise HTTPException(status_code=500, detail="Fallo al guardar el perfil financiero.")

    @staticmethod
    async def obtener_perfil_activo(db: AsyncSession) -> Optional[OnboardingBasico]:
        registros = await onboarding_repo.get_multi(db, limit=1)
        if not registros:
            return None

        perfil = registros[0]
        return OnboardingBasico(
            moneda_principal=perfil.moneda_principal,
            ingreso_mensual_promedio=unidad_menor_a_decimal(perfil.ingreso_mensual_promedio_unidad_menor, perfil.moneda_principal),
            saldo_actual=unidad_menor_a_decimal(perfil.saldo_actual_unidad_menor, perfil.moneda_principal),
            meta_principal=perfil.meta_principal
        )
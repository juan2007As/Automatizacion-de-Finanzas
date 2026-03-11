from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from decimal import Decimal
from datetime import date
from pydantic import BaseModel, Field

from app.models.transaccion import Transaccion
from app.models.categoria import Categoria, TipoCategoria
from app.models.usuario import Usuario
from app.models.onboarding import OnboardingInfo

class DashboardResponse(BaseModel):
    fondo_intocable: Decimal = Field(default=Decimal("0.00"), description="Ahorro/Inversión total acumulada.")
    gastos_hormiga_mes: Decimal = Field(default=Decimal("0.00"), description="Micro-gastos del mes en curso.")
    gastos_eventuales_mes: Decimal = Field(default=Decimal("0.00"), description="Salidas/Antojos mayores del mes.")
    alerta_fuga_capital: bool = Field(default=False, description="True si hormiga+eventual > 20% del ingreso promedio.")
    porcentaje_gastado_deseos: Decimal = Field(default=Decimal("0.00"), description="Porcentaje de salario en antojos.")

class AnalyticsService:
    @staticmethod
    async def get_dashboard_mensual(db: AsyncSession, usuario: Usuario) -> DashboardResponse:
        today = date.today()
        primer_dia_mes = today.replace(day=1)

        stmt_onboarding = select(OnboardingInfo).limit(1)
        result_onboarding = await db.execute(stmt_onboarding)
        perfil = result_onboarding.scalar_one_or_none()

        if perfil:
            ingreso_promedio = Decimal(perfil.ingreso_mensual_promedio_centavos) / Decimal("100")
        else:
            ingreso_promedio = Decimal("0.01")

        stmt_ahorro = select(func.sum(Transaccion.monto_centavos)).join(Categoria).where(
            Categoria.tipo == TipoCategoria.AHORRO_INVERSION
        )
        result_ahorro = await db.execute(stmt_ahorro)
        fondo_total_centavos = result_ahorro.scalar() or 0
        fondo_total = Decimal(fondo_total_centavos) / Decimal("100")

        stmt_gastos = (
            select(Categoria.tipo, func.sum(Transaccion.monto_centavos))
            .join(Transaccion)
            .where(Transaccion.fecha >= primer_dia_mes)
            .where(Categoria.tipo.in_([TipoCategoria.GASTO_HORMIGA, TipoCategoria.GASTO_EVENTUAL]))
            .group_by(Categoria.tipo)
        )
        result_gastos = await db.execute(stmt_gastos)

        gastos_mes_centavos = {row[0]: row[1] or 0 for row in result_gastos.all()}
        hormiga = Decimal(gastos_mes_centavos.get(TipoCategoria.GASTO_HORMIGA, 0)) / Decimal("100")
        eventual = Decimal(gastos_mes_centavos.get(TipoCategoria.GASTO_EVENTUAL, 0)) / Decimal("100")

        total_deseos = hormiga + eventual
        porcentaje_deseos = (total_deseos / ingreso_promedio) * Decimal("100")
        alerta_fuga = porcentaje_deseos > Decimal("20.00")

        return DashboardResponse(
            fondo_intocable=fondo_total.quantize(Decimal('0.00')),
            gastos_hormiga_mes=hormiga.quantize(Decimal('0.00')),
            gastos_eventuales_mes=eventual.quantize(Decimal('0.00')),
            alerta_fuga_capital=alerta_fuga,
            porcentaje_gastado_deseos=porcentaje_deseos.quantize(Decimal('0.00'))
        )

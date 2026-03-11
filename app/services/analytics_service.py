from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from decimal import Decimal
from datetime import date
from pydantic import BaseModel, Field

from app.models.transaccion import Transaccion
from app.models.categoria import Categoria, TipoCategoria
from app.services.onboarding_service import OnboardingService
from app.schemas.moneda_utils import unidad_menor_a_decimal

class DashboardResponse(BaseModel):
    fondo_intocable: Decimal = Field(default=Decimal("0.00"), description="Ahorro total (en la moneda base).")
    gastos_hormiga_mes: Decimal = Field(default=Decimal("0.00"), description="Micro-gastos del mes en curso.")
    gastos_eventuales_mes: Decimal = Field(default=Decimal("0.00"), description="Salidas/Antojos mayores del mes.")
    alerta_fuga_capital: bool = Field(default=False, description="True si hormiga+eventual > 20% del ingreso promedio.")
    porcentaje_gastado_deseos: Decimal = Field(default=Decimal("0.00"), description="Porcentaje de salario en antojos.")
    moneda_base: str = Field(default="USD", description="Moneda en la que se calculan estas métricas.")

class AnalyticsService:
    @staticmethod
    async def get_dashboard_mensual(db: AsyncSession) -> DashboardResponse:
        today = date.today()
        primer_dia_mes = today.replace(day=1)

        perfil = await OnboardingService.obtener_perfil_activo(db)
        if not perfil:
            return DashboardResponse()

        moneda_base = perfil.moneda_principal
        ingreso_promedio = perfil.ingreso_mensual_promedio

        stmt_ahorro = select(func.sum(Transaccion.monto_unidad_menor)).join(Categoria).where(
            Categoria.tipo == TipoCategoria.AHORRO_INVERSION,
            Transaccion.moneda == moneda_base,
            Transaccion.is_active.is_(True)
        )
        result_ahorro = await db.execute(stmt_ahorro)
        fondo_total_unidad_menor = result_ahorro.scalar() or 0
        fondo_total_decimal = unidad_menor_a_decimal(fondo_total_unidad_menor, moneda_base)

        stmt_gastos = (
            select(Categoria.tipo, func.sum(Transaccion.monto_unidad_menor))
            .join(Transaccion)
            .where(
                Transaccion.fecha >= primer_dia_mes,
                Transaccion.moneda == moneda_base,
                Transaccion.is_active.is_(True),
                Categoria.tipo.in_([TipoCategoria.GASTO_HORMIGA, TipoCategoria.GASTO_EVENTUAL])
            )
            .group_by(Categoria.tipo)
        )
        result_gastos = await db.execute(stmt_gastos)

        gastos_mes_unidad_menor = {row[0]: row[1] or 0 for row in result_gastos.all()}

        hormiga_decimal = unidad_menor_a_decimal(gastos_mes_unidad_menor.get(TipoCategoria.GASTO_HORMIGA, 0), moneda_base)
        eventual_decimal = unidad_menor_a_decimal(gastos_mes_unidad_menor.get(TipoCategoria.GASTO_EVENTUAL, 0), moneda_base)

        total_deseos = hormiga_decimal + eventual_decimal

        if ingreso_promedio > Decimal("0"):
            porcentaje_deseos = (total_deseos / ingreso_promedio) * Decimal("100")
        else:
            porcentaje_deseos = Decimal("0")

        alerta_fuga = porcentaje_deseos > Decimal("20.00")

        return DashboardResponse(
            fondo_intocable=fondo_total_decimal.quantize(Decimal('0.00')),
            gastos_hormiga_mes=hormiga_decimal.quantize(Decimal('0.00')),
            gastos_eventuales_mes=eventual_decimal.quantize(Decimal('0.00')),
            alerta_fuga_capital=alerta_fuga,
            porcentaje_gastado_deseos=porcentaje_deseos.quantize(Decimal('0.00')),
            moneda_base=moneda_base
        )
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from app.models.base import Base

class OnboardingInfo(Base):
    """
    Datos iniciales (Punto Cero).
    Soporta una moneda principal (para calcular porcentajes globales).
    """
    moneda_principal: Mapped[str] = mapped_column(String(3), nullable=False)

    # Se guardan en la unidad menor de la moneda principal elegida
    ingreso_mensual_promedio_unidad_menor: Mapped[int] = mapped_column(Integer, nullable=False)
    saldo_actual_unidad_menor: Mapped[int] = mapped_column(Integer, nullable=False)

    meta_principal: Mapped[str | None] = mapped_column(String(255), nullable=True)

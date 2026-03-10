from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Numeric, String
from app.models.base import Base

class OnboardingInfo(Base):
    moneda_principal: Mapped[str] = mapped_column(String(3), nullable=False)
    ingreso_mensual_promedio: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    saldo_actual: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    meta_principal: Mapped[str | None] = mapped_column(String(255), nullable=True)

from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from app.models.base import Base

class OnboardingInfo(Base):
    moneda_principal: Mapped[str] = mapped_column(String(3), nullable=False)
    ingreso_mensual_promedio_centavos: Mapped[int] = mapped_column(Integer, nullable=False)
    saldo_actual_centavos: Mapped[int] = mapped_column(Integer, nullable=False)
    meta_principal: Mapped[str | None] = mapped_column(String(255), nullable=True)

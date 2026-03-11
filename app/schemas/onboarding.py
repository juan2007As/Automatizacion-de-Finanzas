from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from typing import Optional, Any

class OnboardingBasico(BaseModel):
    moneda_principal: str = Field(..., min_length=3, max_length=3)
    ingreso_mensual_promedio: Decimal = Field(..., gt=0)
    saldo_actual: Decimal = Field(...)
    meta_principal: Optional[str] = Field(None, max_length=255)

    @field_validator('moneda_principal')
    @classmethod
    def validar_moneda(cls, v: str) -> str:
        return v.upper()

    @field_validator('ingreso_mensual_promedio', 'saldo_actual', mode='before')
    @classmethod
    def truncar_decimales(cls, v: Any) -> Decimal:
        try:
            val = Decimal(str(v))
            return val.quantize(Decimal('0.00'))
        except Exception:
            raise ValueError("El monto debe ser un número decimal válido.")

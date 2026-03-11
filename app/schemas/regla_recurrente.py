from decimal import Decimal
from datetime import date
from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator
from app.models.regla_recurrente import Frecuencia

class ReglaRecurrenteBase(BaseModel):
    descripcion: str = Field(..., min_length=2, max_length=255)
    monto: Decimal = Field(..., gt=0)
    frecuencia: Frecuencia = Field(...)
    fecha_inicio: date = Field(...)
    fecha_fin: Optional[date] = Field(None)
    categoria_id: int = Field(..., gt=0)

    @field_validator('monto', mode='before')
    @classmethod
    def truncar_decimales(cls, v: Any) -> Decimal:
        try:
            val = Decimal(str(v))
            return val.quantize(Decimal('0.00'))
        except Exception:
            raise ValueError("El monto recurrente debe ser numérico.")

class ReglaRecurrenteCreate(ReglaRecurrenteBase):
    pass

class ReglaRecurrenteResponse(ReglaRecurrenteBase):
    id: int
    ultima_ejecucion: Optional[date]
    is_active: bool
    class Config:
        from_attributes = True

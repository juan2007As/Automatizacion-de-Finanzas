from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class TransaccionBase(BaseModel):
    monto: Decimal = Field(..., gt=0)
    fecha: date = Field(...)
    descripcion: str = Field(..., min_length=2, max_length=255)
    notas: Optional[str] = Field(None)
    categoria_id: int = Field(..., gt=0)

    @field_validator('monto', mode='before')
    @classmethod
    def truncar_decimales(cls, v: any) -> Decimal:
        try:
            val = Decimal(str(v))
            return val.quantize(Decimal('0.00'))
        except Exception:
            raise ValueError("El monto debe ser un número decimal válido.")

class TransaccionCreate(TransaccionBase):
    pass

class TransaccionResponse(BaseModel):
    id: int
    monto: Decimal
    fecha: date
    descripcion: str
    notas: Optional[str] = None
    categoria_id: int

    class Config:
        from_attributes = True

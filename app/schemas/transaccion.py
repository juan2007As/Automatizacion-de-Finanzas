from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.moneda_utils import DIVISAS_SOPORTADAS


class TransaccionBase(BaseModel):
    monto: Decimal = Field(..., gt=0, description="Monto en la divisa original")
    moneda: str = Field(..., min_length=3, max_length=3, description="Código ISO (ej. USD, COP)")
    fecha: date = Field(...)
    descripcion: str = Field(..., min_length=2, max_length=255)
    notas: Optional[str] = Field(None)
    categoria_id: int = Field(..., gt=0)

    @field_validator('moneda')
    @classmethod
    def validar_moneda(cls, v: str) -> str:
        v = v.upper()
        if v not in DIVISAS_SOPORTADAS:
            raise ValueError(f"Divisa {v} no soportada actualmente.")
        return v

    @model_validator(mode='after')
    def validar_decimales_moneda(self) -> 'TransaccionBase':
        decimales_permitidos = DIVISAS_SOPORTADAS.get(self.moneda, 2)
        # Handle the case where exponent is a string or special value (e.g. 'n' for NaN, 'F' for Infinity)
        exponent = self.monto.as_tuple().exponent
        if not isinstance(exponent, int):
            raise ValueError("Monto inválido (NaN o Infinito).")

        if exponent < -decimales_permitidos:
            raise ValueError(
                f"El monto {self.monto} tiene demasiados decimales para la moneda {self.moneda}. "
                f"Máximo permitido: {decimales_permitidos}."
            )
        return self

class TransaccionCreate(TransaccionBase):
    pass

from pydantic import ConfigDict

class TransaccionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    monto: Decimal
    moneda: str
    fecha: date
    descripcion: str
    notas: Optional[str] = None
    categoria_id: int

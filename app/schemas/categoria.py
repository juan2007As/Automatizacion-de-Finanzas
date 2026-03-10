from pydantic import BaseModel, Field
from typing import Optional
from app.models.categoria import TipoCategoria

class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    tipo: TipoCategoria = Field(...)
    color_hex: Optional[str] = Field(default="#008080", pattern=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    color_hex: Optional[str] = Field(None, pattern=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")
    is_active: Optional[bool] = None

class CategoriaResponse(CategoriaBase):
    id: int
    is_active: bool
    class Config:
        from_attributes = True

import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum, Boolean
from app.models.base import Base

class TipoCategoria(str, enum.Enum):
    INGRESO = "INGRESO"
    GASTO_FIJO = "GASTO_FIJO"
    GASTO_EVENTUAL = "GASTO_EVENTUAL"
    GASTO_HORMIGA = "GASTO_HORMIGA"
    AHORRO_INVERSION = "AHORRO_INVERSION"

class Categoria(Base):
    nombre: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    tipo: Mapped[TipoCategoria] = mapped_column(Enum(TipoCategoria), nullable=False)
    color_hex: Mapped[str] = mapped_column(String(7), nullable=True, default="#008080")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    transacciones: Mapped[list["Transaccion"]] = relationship(
        back_populates="categoria", cascade="all, delete-orphan"
    )

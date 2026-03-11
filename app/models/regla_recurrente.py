import enum
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum, Integer, Date, Boolean, ForeignKey
from app.models.base import Base

class Frecuencia(str, enum.Enum):
    DIARIO = "DIARIO"
    SEMANAL = "SEMANAL"
    QUINCENAL = "QUINCENAL"
    MENSUAL = "MENSUAL"
    ANUAL = "ANUAL"

class ReglaRecurrente(Base):
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)
    monto_centavos: Mapped[int] = mapped_column(Integer, nullable=False)
    frecuencia: Mapped[Frecuencia] = mapped_column(Enum(Frecuencia), nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    ultima_ejecucion: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    categoria: Mapped["Categoria"] = relationship() # noqa: F821

from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, Date, ForeignKey, Index
from app.models.base import Base
import app.models.categoria

class Transaccion(Base):
    monto_unidad_menor: Mapped[int] = mapped_column(Integer, nullable=False)
    moneda: Mapped[str] = mapped_column(String(3), index=True, nullable=False)
    fecha: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)

    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    categoria: Mapped["app.models.categoria.Categoria"] = relationship(back_populates="transacciones")

    __table_args__ = (
        Index("ix_transacciones_fecha_cat", "fecha", "categoria_id"),
        Index("ix_transacciones_moneda", "moneda"),
    )

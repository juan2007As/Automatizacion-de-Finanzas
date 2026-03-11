from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, Date, ForeignKey, Index
from app.models.base import Base

class Transaccion(Base):
    # En SQLite, guardar Decimal/Numeric puede causar pérdida de precisión.
    # El dinero se guardará como Integer (centavos). Ej. 15.50 -> 1550.
    # La API lo convertirá a Decimal al responder.
    monto_centavos: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)

    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    categoria: Mapped["Categoria"] = relationship(back_populates="transacciones")

    __table_args__ = (
        Index("ix_transacciones_fecha_cat", "fecha", "categoria_id"),
    )

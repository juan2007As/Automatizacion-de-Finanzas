from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean
from app.models.base import Base

class Usuario(Base):
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    # Al estar en SQLite (mono-usuario/mono-db), este campo es residual.
    # Quitamos unique=True para que puedan registrarse múltiples usuarios si usan el mismo equipo local.
    tenant_schema: Mapped[str] = mapped_column(String(100), unique=False, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)

#!/bin/bash
# Backup/Restore Script: Garantiza que la estructura y código del Automatizador Financiero estén completos.
# Generado para proteger el proyecto de pérdidas en el sandbox.

mkdir -p app/{core,models,schemas,routers,services,db,api} tests migrations
touch app/__init__.py tests/__init__.py

# --- CORE ---
cat << 'EOF' > app/core/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "Automatizador de Finanzas Personales"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    POSTGRES_SERVER: str = Field(default="localhost", env="POSTGRES_SERVER")
    POSTGRES_USER: str = Field(default="postgres", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="postgres", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(default="finanzas_db", env="POSTGRES_DB")
    POSTGRES_PORT: str = Field(default="5432", env="POSTGRES_PORT")

    SECRET_KEY: str = Field(default="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def async_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()
EOF

cat << 'EOF' > app/core/logger.py
import json
import logging
import traceback
from datetime import datetime
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineNo": record.lineno,
        }
        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
            log_record["stack_trace"] = traceback.format_exc()
        if hasattr(record, "context"):
            log_record["context"] = record.context
        return json.dumps(log_record)

def setup_logger(name: str = "finanzas_app", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
    logger.propagate = False
    return logger

logger = setup_logger()
EOF

cat << 'EOF' > app/core/security.py
from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
EOF

# --- DB ---
cat << 'EOF' > app/db/session.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.core.config import settings
from app.core.logger import logger

engine = create_async_engine(
    settings.async_database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_tenant_db_session(schema_name: str) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(text(f'SET search_path TO "{schema_name}"'))
            yield session
        except Exception as e:
            logger.error(f"Error configurando el tenant schema {schema_name}: {str(e)}")
            raise
        finally:
            await session.close()
EOF

# --- MODELS ---
cat << 'EOF' > app/models/base.py
from typing import Any
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    @classmethod
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"
EOF

cat << 'EOF' > app/models/usuario.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean
from app.models.base import Base

class Usuario(Base):
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    tenant_schema: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)
EOF

cat << 'EOF' > app/models/categoria.py
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
EOF

cat << 'EOF' > app/models/transaccion.py
from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Numeric, String, Text, Date, ForeignKey, Index
from app.models.base import Base

class Transaccion(Base):
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
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
EOF

cat << 'EOF' > app/models/regla_recurrente.py
import enum
from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum, Numeric, Date, Boolean, ForeignKey
from app.models.base import Base

class Frecuencia(str, enum.Enum):
    DIARIO = "DIARIO"
    SEMANAL = "SEMANAL"
    QUINCENAL = "QUINCENAL"
    MENSUAL = "MENSUAL"
    ANUAL = "ANUAL"

class ReglaRecurrente(Base):
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    frecuencia: Mapped[Frecuencia] = mapped_column(Enum(Frecuencia), nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    ultima_ejecucion: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    categoria: Mapped["Categoria"] = relationship()
EOF

cat << 'EOF' > app/models/onboarding.py
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Numeric, String
from app.models.base import Base

class OnboardingInfo(Base):
    moneda_principal: Mapped[str] = mapped_column(String(3), nullable=False)
    ingreso_mensual_promedio: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    saldo_actual: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    meta_principal: Mapped[str | None] = mapped_column(String(255), nullable=True)
EOF

cat << 'EOF' > app/models/__init__.py
from app.models.base import Base
from app.models.usuario import Usuario
from app.models.categoria import Categoria
from app.models.transaccion import Transaccion
from app.models.regla_recurrente import ReglaRecurrente
from app.models.onboarding import OnboardingInfo
EOF

# --- SCHEMAS ---
cat << 'EOF' > app/schemas/usuario.py
from pydantic import BaseModel, EmailStr, Field

class UsuarioBase(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico del usuario")

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8, description="Contraseña segura (mín. 8 caracteres)")

class UsuarioResponse(UsuarioBase):
    id: int
    is_active: bool
    onboarding_completed: bool
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str | None = None
EOF

cat << 'EOF' > app/schemas/onboarding.py
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from typing import Optional

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
    def truncar_decimales(cls, v: any) -> Decimal:
        try:
            val = Decimal(str(v))
            return val.quantize(Decimal('0.00'))
        except Exception:
            raise ValueError("El monto debe ser un número decimal válido.")
EOF

cat << 'EOF' > app/schemas/categoria.py
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
EOF

cat << 'EOF' > app/schemas/transaccion.py
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

class TransaccionResponse(TransaccionBase):
    id: int
    class Config:
        from_attributes = True
EOF

cat << 'EOF' > app/schemas/regla_recurrente.py
from decimal import Decimal
from datetime import date
from typing import Optional
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
    def truncar_decimales(cls, v: any) -> Decimal:
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
EOF

# --- SERVICES ---
cat << 'EOF' > app/services/tenant_manager.py
import uuid
from sqlalchemy import text
from app.db.session import engine
from app.core.logger import logger
from app.models.base import Base
import app.models.categoria
import app.models.transaccion
import app.models.regla_recurrente
import app.models.onboarding

class TenantManager:
    @staticmethod
    def generate_tenant_name(user_id: int) -> str:
        random_suffix = uuid.uuid4().hex[:8]
        return f"tenant_user_{user_id}_{random_suffix}"

    @staticmethod
    async def create_tenant_schema(schema_name: str) -> None:
        async with engine.begin() as conn:
            try:
                await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
                await conn.execute(text(f'SET search_path TO "{schema_name}"'))

                tables_to_create = [
                    Base.metadata.tables[table_name]
                    for table_name in Base.metadata.tables
                    if table_name != "usuarios"
                ]

                await conn.run_sync(Base.metadata.create_all, tables=tables_to_create)
            except Exception as e:
                logger.error(f"Fallo crítico al crear el tenant schema '{schema_name}': {str(e)}")
                raise
EOF

cat << 'EOF' > app/services/analytics.py
from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from decimal import Decimal
from datetime import date
from pydantic import BaseModel, Field

from app.models.transaccion import Transaccion
from app.models.categoria import Categoria, TipoCategoria
from app.models.usuario import Usuario
from app.models.onboarding import OnboardingInfo

class DashboardResponse(BaseModel):
    fondo_intocable: Decimal = Field(default=Decimal("0.00"), description="Ahorro/Inversión total acumulada.")
    gastos_hormiga_mes: Decimal = Field(default=Decimal("0.00"), description="Micro-gastos del mes en curso.")
    gastos_eventuales_mes: Decimal = Field(default=Decimal("0.00"), description="Salidas/Antojos mayores del mes.")
    alerta_fuga_capital: bool = Field(default=False, description="True si hormiga+eventual > 20% del ingreso promedio.")
    porcentaje_gastado_deseos: Decimal = Field(default=Decimal("0.00"), description="Porcentaje de salario en antojos.")

class AnalyticsService:
    @staticmethod
    async def get_dashboard_mensual(db: AsyncSession, usuario: Usuario) -> DashboardResponse:
        today = date.today()
        primer_dia_mes = today.replace(day=1)

        stmt_onboarding = select(OnboardingInfo).limit(1)
        result_onboarding = await db.execute(stmt_onboarding)
        perfil = result_onboarding.scalar_one_or_none()

        ingreso_promedio = perfil.ingreso_mensual_promedio if perfil else Decimal("0.01")

        stmt_ahorro = select(func.sum(Transaccion.monto)).join(Categoria).where(
            Categoria.tipo == TipoCategoria.AHORRO_INVERSION
        )
        result_ahorro = await db.execute(stmt_ahorro)
        fondo_total = result_ahorro.scalar() or Decimal("0.00")

        stmt_gastos = (
            select(Categoria.tipo, func.sum(Transaccion.monto))
            .join(Transaccion)
            .where(Transaccion.fecha >= primer_dia_mes)
            .where(Categoria.tipo.in_([TipoCategoria.GASTO_HORMIGA, TipoCategoria.GASTO_EVENTUAL]))
            .group_by(Categoria.tipo)
        )
        result_gastos = await db.execute(stmt_gastos)

        gastos_mes = {row[0]: row[1] or Decimal("0.00") for row in result_gastos.all()}
        hormiga = gastos_mes.get(TipoCategoria.GASTO_HORMIGA, Decimal("0.00"))
        eventual = gastos_mes.get(TipoCategoria.GASTO_EVENTUAL, Decimal("0.00"))

        total_deseos = hormiga + eventual
        porcentaje_deseos = (total_deseos / ingreso_promedio) * Decimal("100")
        alerta_fuga = porcentaje_deseos > Decimal("20.00")

        return DashboardResponse(
            fondo_intocable=fondo_total.quantize(Decimal('0.00')),
            gastos_hormiga_mes=hormiga.quantize(Decimal('0.00')),
            gastos_eventuales_mes=eventual.quantize(Decimal('0.00')),
            alerta_fuga_capital=alerta_fuga,
            porcentaje_gastado_deseos=porcentaje_deseos.quantize(Decimal('0.00'))
        )
EOF

# --- API DEPS ---
cat << 'EOF' > app/api/deps.py
from typing import Generator, AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.db.session import get_db_session, get_tenant_db_session
from app.models.usuario import Usuario
from app.schemas.usuario import TokenPayload
from app.core.logger import logger

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

async def get_current_user(
    db: AsyncSession = Depends(get_db_session),
    token: str = Depends(reusable_oauth2)
) -> Usuario:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError) as e:
        logger.error(f"Fallo de validación de JWT: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token inválido o expirado.",
        )
    stmt = select(Usuario).where(Usuario.id == int(token_data.sub))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user: raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if not user.is_active: raise HTTPException(status_code=400, detail="Usuario inactivo.")
    return user

async def get_current_active_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    return current_user

async def get_current_tenant_db(current_user: Usuario = Depends(get_current_active_user)) -> AsyncGenerator[AsyncSession, None]:
    async for db in get_tenant_db_session(current_user.tenant_schema):
        yield db
EOF

# --- ROUTERS ---
cat << 'EOF' > app/routers/auth.py
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db_session
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.services.tenant_manager import TenantManager

router = APIRouter()

@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UsuarioCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db_session)):
    stmt = select(Usuario).where(Usuario.email == user_in.email)
    if (await db.execute(stmt)).scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email ya existe.")

    hashed_password = get_password_hash(user_in.password)
    new_user = Usuario(email=user_in.email, hashed_password=hashed_password, tenant_schema="pending_schema")
    db.add(new_user)
    await db.flush()

    tenant_name = TenantManager.generate_tenant_name(new_user.id)
    new_user.tenant_schema = tenant_name
    await db.commit()
    await db.refresh(new_user)

    background_tasks.add_task(TenantManager.create_tenant_schema, tenant_name)
    return new_user

@router.post("/login/access-token", response_model=Token)
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db_session)):
    stmt = select(Usuario).where(Usuario.email == form_data.username)
    user = (await db.execute(stmt)).scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Credenciales incorrectas.")

    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}
EOF

cat << 'EOF' > app/routers/categorias.py
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_tenant_db
from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate, CategoriaResponse

router = APIRouter()

@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
async def create_categoria(categoria_in: CategoriaCreate, db: AsyncSession = Depends(get_current_tenant_db)):
    stmt = select(Categoria).where(Categoria.nombre == categoria_in.nombre)
    if (await db.execute(stmt)).scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Categoría ya existe.")

    nueva = Categoria(**categoria_in.model_dump())
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return nueva

@router.get("/", response_model=List[CategoriaResponse])
async def read_categorias(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_current_tenant_db)):
    stmt = select(Categoria).where(Categoria.is_active == True).offset(skip).limit(limit)
    return (await db.execute(stmt)).scalars().all()
EOF

cat << 'EOF' > app/routers/transacciones.py
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_tenant_db
from app.models.transaccion import Transaccion
from app.models.categoria import Categoria
from app.schemas.transaccion import TransaccionCreate, TransaccionResponse

router = APIRouter()

@router.post(
    "/",
    response_model=TransaccionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nueva transacción",
    description="Crea un ingreso o gasto real en el mes actual. Solo acepta montos decimales exactos.",
    responses={
        422: {
            "description": "Error de Validación (Regla 3). El monto no es un número válido.",
            "content": {"application/json": {"example": {"detail": "Error en formato", "sugerencia_amigable": "¿Quisiste decir 150.00?"}}}
        }
    }
)
async def create_transaccion(transaccion_in: TransaccionCreate, db: AsyncSession = Depends(get_current_tenant_db)):
    stmt_cat = select(Categoria).where(Categoria.id == transaccion_in.categoria_id)
    categoria = (await db.execute(stmt_cat)).scalar_one_or_none()

    if not categoria or not categoria.is_active:
        raise HTTPException(status_code=404, detail="Categoría no encontrada o inactiva.")

    nueva_tx = Transaccion(**transaccion_in.model_dump())
    db.add(nueva_tx)
    await db.commit()
    await db.refresh(nueva_tx)
    return nueva_tx

@router.get("/", response_model=List[TransaccionResponse])
async def read_transacciones(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_current_tenant_db)):
    stmt = select(Transaccion).order_by(Transaccion.fecha.desc()).offset(skip).limit(limit)
    return (await db.execute(stmt)).scalars().all()
EOF

cat << 'EOF' > app/routers/reglas_recurrentes.py
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_tenant_db
from app.models.regla_recurrente import ReglaRecurrente
from app.models.categoria import Categoria
from app.schemas.regla_recurrente import ReglaRecurrenteCreate, ReglaRecurrenteResponse

router = APIRouter()

@router.post("/", response_model=ReglaRecurrenteResponse, status_code=status.HTTP_201_CREATED)
async def create_regla(regla_in: ReglaRecurrenteCreate, db: AsyncSession = Depends(get_current_tenant_db)):
    nueva = ReglaRecurrente(**regla_in.model_dump())
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return nueva
EOF

cat << 'EOF' > app/routers/onboarding.py
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_tenant_db, get_current_active_user, get_db_session
from app.models.usuario import Usuario
from app.models.onboarding import OnboardingInfo
from app.schemas.onboarding import OnboardingBasico

router = APIRouter()

@router.post("/", response_model=OnboardingBasico, status_code=status.HTTP_201_CREATED)
async def setup_onboarding(
    onboarding_data: OnboardingBasico,
    current_user: Usuario = Depends(get_current_active_user),
    db_tenant: AsyncSession = Depends(get_current_tenant_db),
    db_public: AsyncSession = Depends(get_db_session)
):
    stmt_check = select(OnboardingInfo).limit(1)
    if (await db_tenant.execute(stmt_check)).scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Onboarding ya completado.")

    nuevo_perfil = OnboardingInfo(**onboarding_data.model_dump())
    db_tenant.add(nuevo_perfil)
    await db_tenant.commit()

    stmt_user = select(Usuario).where(Usuario.id == current_user.id)
    user_to_update = (await db_public.execute(stmt_user)).scalar_one()
    user_to_update.onboarding_completed = True
    await db_public.commit()

    return onboarding_data
EOF

cat << 'EOF' > app/routers/analytics.py
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant_db, get_current_active_user
from app.models.usuario import Usuario
from app.services.analytics import AnalyticsService, DashboardResponse

router = APIRouter()

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard_principal(
    current_user: Usuario = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_current_tenant_db)
):
    return await AnalyticsService.get_dashboard_mensual(db, current_user)
EOF

cat << 'EOF' > app/routers/__init__.py
from fastapi import APIRouter
from app.routers import auth, categorias, transacciones, reglas_recurrentes, onboarding, analytics

api_router = APIRouter()
api_router.include_router(auth.router, tags=["Autenticación"])
api_router.include_router(onboarding.router, prefix="/onboarding", tags=["Punto Cero"])
api_router.include_router(categorias.router, prefix="/categorias", tags=["Categorías (Sobres)"])
api_router.include_router(transacciones.router, prefix="/transacciones", tags=["Transacciones (Flujo)"])
api_router.include_router(reglas_recurrentes.router, prefix="/suscripciones", tags=["Motor Recurrente (Zombis/Diezmo)"])
api_router.include_router(analytics.router, prefix="/analitica", tags=["Dashboard KPIs"])
EOF

# --- MAIN ---
cat << 'EOF' > app/main.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.core.logger import logger
from app.routers import api_router

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Error en el formato de los datos.",
                "errores_tecnicos": exc.errors(),
                "sugerencia_amigable": "Revisa que los montos sean decimales correctos."
            },
        )

    @application.get("/health", tags=["Sistema"])
    async def health_check():
        return {"status": "ok"}

    application.include_router(api_router, prefix=settings.API_V1_STR)
    return application

app = create_application()
EOF

echo "¡Estructura Backend Completamente Restaurada y Protegida!"

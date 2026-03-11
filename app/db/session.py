from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# SQLite asíncrono. No soporta pool sizes como postgres, es local mono-archivo.
engine = create_async_engine(
    settings.async_database_url,
    echo=False,
    # SQLite no usa pool_size ni max_overflow
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

# get_tenant_db_session ELIMINADA. Ya no usamos Multi-Tenancy (Schemas de Postgres).
# La base de datos entera le pertenece a la persona que instala la app offline.

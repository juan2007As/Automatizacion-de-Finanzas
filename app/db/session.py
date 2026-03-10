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
            # Evitamos inyección de SQL validando y escapando comillas en identificadores.
            safe_schema = schema_name.replace('"', '""')
            await session.execute(text(f'SET search_path TO "{safe_schema}"'))
            yield session
        except Exception as e:
            logger.error(f"Error configurando el tenant schema {schema_name}: {str(e)}")
            raise
        finally:
            await session.close()

import asyncio
from app.db.session import engine
from app.models.base import Base
import app.models

async def init_db():
    """
    Inicializa la base de datos de SQLite.
    PELIGRO: NUNCA hacer drop_all en un entorno de producción o local del usuario,
    eso borraría todo el historial financiero.
    """
    async with engine.begin() as conn:
        # Crea las tablas solo si no existen previamente
        await conn.run_sync(Base.metadata.create_all)
        print("Migraciones ejecutadas: Base de datos lista.")

if __name__ == "__main__":
    asyncio.run(init_db())

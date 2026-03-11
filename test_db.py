import asyncio
from app.db.session import engine
from app.models.base import Base
import app.models  # Ensures all models are imported so Base metadata registers them

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("Tablas creadas exitosamente en SQLite.")

if __name__ == "__main__":
    asyncio.run(init_db())

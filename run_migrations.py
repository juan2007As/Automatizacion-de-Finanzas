import asyncio
from app.db.session import engine
from app.models.base import Base
import app.models

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("Tablas creadas exitosamente en SQLite (V5).")

if __name__ == "__main__":
    asyncio.run(init_db())

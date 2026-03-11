from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.repositories.base import BaseRepository
from app.models.transaccion import Transaccion

class TransaccionRepository(BaseRepository[Transaccion]):
    async def get_by_categoria(
        self, db: AsyncSession, categoria_id: int, skip: int = 0, limit: int = 100
    ) -> List[Transaccion]:
        stmt = select(Transaccion).where(
            Transaccion.categoria_id == categoria_id,
            Transaccion.is_active.is_(True)
        ).order_by(Transaccion.fecha.desc()).offset(skip).limit(limit)

        result = await db.execute(stmt)
        return list(result.scalars().all())

transaccion_repo = TransaccionRepository(Transaccion)

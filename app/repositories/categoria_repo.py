from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.categoria import Categoria
from app.repositories.base import BaseRepository


class CategoriaRepository(BaseRepository[Categoria]):
    async def get_by_name(self, db: AsyncSession, nombre: str) -> Optional[Categoria]:
        stmt = select(Categoria).where(
            Categoria.nombre == nombre,
            Categoria.is_active.is_(True)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

categoria_repo = CategoriaRepository(Categoria)

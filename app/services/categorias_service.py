from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCreate
from app.repositories.categoria_repo import categoria_repo
from app.core.logger import logger

class CategoriaService:
    @staticmethod
    async def create_categoria(db: AsyncSession, categoria_in: CategoriaCreate) -> Categoria:
        existente = await categoria_repo.get_by_name(db, nombre=categoria_in.nombre)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una categoría con ese nombre."
            )

        try:
            nueva_cat = await categoria_repo.create(db, obj_in=categoria_in.model_dump())
            await db.commit()
            await db.refresh(nueva_cat)
            logger.info(f"Categoría creada: {nueva_cat.nombre}")
            return nueva_cat
        except Exception as e:
            await db.rollback()
            logger.error(f"Fallo al crear categoría: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Fallo interno al guardar la categoría.")

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Categoria]:
        return await categoria_repo.get_multi(db, skip=skip, limit=limit)

    @staticmethod
    async def soft_delete(db: AsyncSession, categoria_id: int) -> None:
        cat = await categoria_repo.get(db, id=categoria_id)
        if not cat:
            raise HTTPException(status_code=404, detail="Categoría no encontrada.")

        await categoria_repo.remove(db, id=categoria_id)
        await db.commit()
        logger.info(f"Categoría Soft-Deleted: ID {categoria_id}")
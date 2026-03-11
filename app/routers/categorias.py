from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db_session
from app.schemas.categoria import CategoriaCreate, CategoriaResponse
from app.services.categorias_service import CategoriaService

router = APIRouter()

@router.post(
    "/",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear Categoría (Sobre)",
    description="Crea un nuevo contenedor o sobre para agrupar transacciones (ej. 'Gastos Hormiga', 'Sueldo').",
    responses={
        400: {"description": "El nombre de la categoría ya existe."}
    }
)
async def crear_categoria(
    payload_categoria: CategoriaCreate,
    db: AsyncSession = Depends(get_db_session)
):
    # Pilar 2: El Router solo delega, no calcula.
    return await CategoriaService.create_categoria(db, payload_categoria)

@router.get(
    "/",
    response_model=List[CategoriaResponse],
    summary="Listar Categorías Activas",
)
async def listar_categorias(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    return await CategoriaService.get_all(db, skip, limit)

@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar Categoría",
    description="Aplica un Soft Delete. La categoría dejará de estar disponible para nuevas transacciones, pero no romperá el historial pasado."
)
async def eliminar_categoria(
    categoria_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    await CategoriaService.soft_delete(db, categoria_id)

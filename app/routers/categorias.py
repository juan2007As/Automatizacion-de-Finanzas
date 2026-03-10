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

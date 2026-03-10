from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_tenant_db
from app.models.transaccion import Transaccion
from app.models.categoria import Categoria
from app.schemas.transaccion import TransaccionCreate, TransaccionResponse

router = APIRouter()

@router.post(
    "/",
    response_model=TransaccionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nueva transacción",
    description="Crea un ingreso o gasto real en el mes actual. Solo acepta montos decimales exactos.",
    responses={
        422: {
            "description": "Error de Validación (Regla 3). El monto no es un número válido.",
            "content": {"application/json": {"example": {"detail": "Error en formato", "sugerencia_amigable": "¿Quisiste decir 150.00?"}}}
        }
    }
)
async def create_transaccion(transaccion_in: TransaccionCreate, db: AsyncSession = Depends(get_current_tenant_db)):
    stmt_cat = select(Categoria).where(Categoria.id == transaccion_in.categoria_id)
    categoria = (await db.execute(stmt_cat)).scalar_one_or_none()

    if not categoria or not categoria.is_active:
        raise HTTPException(status_code=404, detail="Categoría no encontrada o inactiva.")

    nueva_tx = Transaccion(**transaccion_in.model_dump())
    db.add(nueva_tx)
    await db.commit()
    await db.refresh(nueva_tx)
    return nueva_tx

@router.get("/", response_model=List[TransaccionResponse])
async def read_transacciones(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_current_tenant_db)):
    stmt = select(Transaccion).order_by(Transaccion.fecha.desc()).offset(skip).limit(limit)
    return (await db.execute(stmt)).scalars().all()

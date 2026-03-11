from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from decimal import Decimal
from app.api.deps import get_db_session, get_current_active_user
from app.models.transaccion import Transaccion
from app.models.categoria import Categoria
from app.models.usuario import Usuario
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
async def create_transaccion(
    transaccion_in: TransaccionCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_active_user)
):
    stmt_cat = select(Categoria).where(Categoria.id == transaccion_in.categoria_id)
    categoria = (await db.execute(stmt_cat)).scalar_one_or_none()

    if not categoria or not categoria.is_active:
        raise HTTPException(status_code=404, detail="Categoría no encontrada o inactiva.")

    # Guardamos convirtiendo el Decimal Pydantic a centavos Integer para SQLite
    centavos = int(transaccion_in.monto * Decimal("100"))
    nueva_tx = Transaccion(
        monto_centavos=centavos,
        fecha=transaccion_in.fecha,
        descripcion=transaccion_in.descripcion,
        notas=transaccion_in.notas,
        categoria_id=transaccion_in.categoria_id
    )
    db.add(nueva_tx)
    await db.commit()
    await db.refresh(nueva_tx)

    # Retornamos el schema response con la conversion on-the-fly
    return TransaccionResponse(
        id=nueva_tx.id,
        monto=Decimal(nueva_tx.monto_centavos) / Decimal("100"),
        fecha=nueva_tx.fecha,
        descripcion=nueva_tx.descripcion,
        notas=nueva_tx.notas,
        categoria_id=nueva_tx.categoria_id
    )

@router.get("/", response_model=List[TransaccionResponse])
async def read_transacciones(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
    current_user: Usuario = Depends(get_current_active_user)
):
    stmt = select(Transaccion).order_by(Transaccion.fecha.desc()).offset(skip).limit(limit)
    transacciones_db = (await db.execute(stmt)).scalars().all()

    return [
        TransaccionResponse(
            id=tx.id,
            monto=Decimal(tx.monto_centavos) / Decimal("100"),
            fecha=tx.fecha,
            descripcion=tx.descripcion,
            notas=tx.notas,
            categoria_id=tx.categoria_id
        ) for tx in transacciones_db
    ]

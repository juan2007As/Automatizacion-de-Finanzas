from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from decimal import Decimal
from app.api.deps import get_db_session, get_current_active_user
from app.models.usuario import Usuario
from app.models.regla_recurrente import ReglaRecurrente
from app.models.categoria import Categoria
from app.schemas.regla_recurrente import ReglaRecurrenteCreate, ReglaRecurrenteResponse

router = APIRouter()

@router.post("/", response_model=ReglaRecurrenteResponse, status_code=status.HTTP_201_CREATED)
async def create_regla(regla_in: ReglaRecurrenteCreate, db: AsyncSession = Depends(get_db_session), current_user: Usuario = Depends(get_current_active_user)):
    centavos = int(regla_in.monto * Decimal("100"))

    nueva = ReglaRecurrente(
        descripcion=regla_in.descripcion,
        monto_centavos=centavos,
        frecuencia=regla_in.frecuencia,
        fecha_inicio=regla_in.fecha_inicio,
        fecha_fin=regla_in.fecha_fin,
        categoria_id=regla_in.categoria_id
    )
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)

    return ReglaRecurrenteResponse(
        id=nueva.id,
        descripcion=nueva.descripcion,
        monto=Decimal(nueva.monto_centavos) / Decimal("100"),
        frecuencia=nueva.frecuencia,
        fecha_inicio=nueva.fecha_inicio,
        fecha_fin=nueva.fecha_fin,
        categoria_id=nueva.categoria_id,
        ultima_ejecucion=nueva.ultima_ejecucion,
        is_active=nueva.is_active
    )

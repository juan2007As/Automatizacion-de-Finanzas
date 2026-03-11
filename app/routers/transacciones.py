from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.transaccion import TransaccionCreate, TransaccionResponse
from app.services.transacciones_service import TransaccionService

router = APIRouter()

@router.post(
    "/",
    response_model=TransaccionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar Flujo de Caja",
    description="Inserta un ingreso o gasto. El sistema convierte automáticamente la divisa (`monto`) a su unidad mínima según la moneda (ej. COP vs USD) para preservar precisión financiera sin usar float.",
    responses={
        422: {"description": "El tipo de dato es incorrecto o la moneda no soporta los decimales enviados."},
        404: {"description": "La `categoria_id` proporcionada no existe o fue eliminada."}
    }
)
async def crear_transaccion(
    payload_transaccion: TransaccionCreate,
    db: AsyncSession = Depends(get_db_session)
) -> TransaccionResponse:
    return await TransaccionService.registrar_transaccion(db, payload_transaccion)

@router.get(
    "/",
    response_model=List[TransaccionResponse],
    summary="Historial de Transacciones",
    description="Devuelve el historial en orden cronológico inverso."
)
async def obtener_historial(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
) -> List[TransaccionResponse]:
    return await TransaccionService.listar_historial(db, skip, limit)

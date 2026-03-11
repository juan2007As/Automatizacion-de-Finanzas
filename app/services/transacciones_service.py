from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.repositories.categoria_repo import categoria_repo
from app.repositories.transaccion_repo import transaccion_repo
from app.schemas.moneda_utils import decimal_a_unidad_menor, unidad_menor_a_decimal
from app.schemas.transaccion import TransaccionCreate, TransaccionResponse


class TransaccionService:
    @staticmethod
    async def registrar_transaccion(db: AsyncSession, payload_tx: TransaccionCreate) -> TransaccionResponse:
        categoria = await categoria_repo.get(db, id=payload_tx.categoria_id)
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La categoría asignada no existe o está inactiva."
            )

        monto_sqlite = decimal_a_unidad_menor(payload_tx.monto, payload_tx.moneda)

        tx_data = {
            "monto_unidad_menor": monto_sqlite,
            "moneda": payload_tx.moneda,
            "fecha": payload_tx.fecha,
            "descripcion": payload_tx.descripcion,
            "notas": payload_tx.notas,
            "categoria_id": payload_tx.categoria_id
        }

        try:
            nueva_tx = await transaccion_repo.create(db, obj_in=tx_data)
            await db.commit()
            await db.refresh(nueva_tx)
            logger.info(f"Transacción {nueva_tx.id} registrada: {payload_tx.monto} {payload_tx.moneda}")

            return TransaccionResponse(
                id=nueva_tx.id,
                monto=payload_tx.monto,
                moneda=nueva_tx.moneda,
                fecha=nueva_tx.fecha,
                descripcion=nueva_tx.descripcion,
                notas=nueva_tx.notas,
                categoria_id=nueva_tx.categoria_id
            )
        except Exception as e:
            await db.rollback()
            logger.error(f"Error guardando transacción ACID: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Fallo al registrar la transacción.") from e

    @staticmethod
    async def listar_historial(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[TransaccionResponse]:
        transacciones_bd = await transaccion_repo.get_multi(db, skip=skip, limit=limit)

        resultado_formateado = []
        for tx in transacciones_bd:
            monto_visual = unidad_menor_a_decimal(tx.monto_unidad_menor, tx.moneda)

            resultado_formateado.append(
                TransaccionResponse(
                    id=tx.id,
                    monto=monto_visual,
                    moneda=tx.moneda,
                    fecha=tx.fecha,
                    descripcion=tx.descripcion,
                    notas=tx.notas,
                    categoria_id=tx.categoria_id
                )
            )
        return resultado_formateado

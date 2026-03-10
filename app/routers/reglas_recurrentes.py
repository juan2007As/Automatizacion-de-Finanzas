from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_tenant_db
from app.models.regla_recurrente import ReglaRecurrente
from app.models.categoria import Categoria
from app.schemas.regla_recurrente import ReglaRecurrenteCreate, ReglaRecurrenteResponse

router = APIRouter()

@router.post("/", response_model=ReglaRecurrenteResponse, status_code=status.HTTP_201_CREATED)
async def create_regla(regla_in: ReglaRecurrenteCreate, db: AsyncSession = Depends(get_current_tenant_db)):
    nueva = ReglaRecurrente(**regla_in.model_dump())
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return nueva

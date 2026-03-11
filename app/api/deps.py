from typing import Generator, AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.db.session import get_db_session
from app.models.usuario import Usuario
from app.schemas.usuario import TokenPayload
from app.core.logger import logger

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

async def get_current_user(
    db: AsyncSession = Depends(get_db_session),
    token: str = Depends(reusable_oauth2)
) -> Usuario:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError) as e:
        logger.error(f"Fallo de validación de JWT: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token inválido o expirado.",
        )
    stmt = select(Usuario).where(Usuario.id == int(token_data.sub))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user: raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if not user.is_active: raise HTTPException(status_code=400, detail="Usuario inactivo.")
    return user

async def get_current_active_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    return current_user

# get_current_tenant_db Eliminado, se usará `get_db_session` directamente + `current_user`

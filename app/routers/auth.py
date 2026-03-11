from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db_session
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, Token
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UsuarioCreate, db: AsyncSession = Depends(get_db_session)):
    stmt = select(Usuario).where(Usuario.email == user_in.email)
    if (await db.execute(stmt)).scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email ya existe.")

    hashed_password = get_password_hash(user_in.password)
    new_user = Usuario(email=user_in.email, hashed_password=hashed_password, tenant_schema="local_sqlite_schema")
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.post("/login/access-token", response_model=Token)
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db_session)):
    stmt = select(Usuario).where(Usuario.email == form_data.username)
    user = (await db.execute(stmt)).scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Credenciales incorrectas.")

    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}

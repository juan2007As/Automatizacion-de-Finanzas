from pydantic import BaseModel, EmailStr, Field

class UsuarioBase(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico del usuario")

class UsuarioCreate(UsuarioBase):
    # Límite estricto de 72 caracteres de bcrypt
    password: str = Field(..., min_length=8, max_length=72, description="Contraseña segura (mín. 8 caracteres, máx. 72)")

class UsuarioResponse(UsuarioBase):
    id: int
    is_active: bool
    onboarding_completed: bool
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str | None = None

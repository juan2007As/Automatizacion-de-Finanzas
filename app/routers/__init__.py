from fastapi import APIRouter
from app.routers import auth, categorias, transacciones, reglas_recurrentes, onboarding, analytics

api_router = APIRouter()
api_router.include_router(auth.router, tags=["Autenticación"])
api_router.include_router(onboarding.router, prefix="/onboarding", tags=["Punto Cero"])
api_router.include_router(categorias.router, prefix="/categorias", tags=["Categorías (Sobres)"])
api_router.include_router(transacciones.router, prefix="/transacciones", tags=["Transacciones (Flujo)"])
api_router.include_router(reglas_recurrentes.router, prefix="/suscripciones", tags=["Motor Recurrente (Zombis/Diezmo)"])
api_router.include_router(analytics.router, prefix="/analitica", tags=["Dashboard KPIs"])

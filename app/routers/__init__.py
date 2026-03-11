from fastapi import APIRouter

from app.routers import analytics, categorias, onboarding, transacciones

api_router = APIRouter()

api_router.include_router(onboarding.router, prefix="/onboarding", tags=["Configuración Inicial"])
api_router.include_router(categorias.router, prefix="/categorias", tags=["Categorías"])
api_router.include_router(transacciones.router, prefix="/transacciones", tags=["Transacciones"])
api_router.include_router(analytics.router, prefix="/analitica", tags=["Dashboard KPIs"])

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.core.logger import logger
from app.routers import api_router

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Error en el formato de los datos.",
                "errores_tecnicos": exc.errors(),
                "sugerencia_amigable": "Revisa que los montos sean decimales correctos."
            },
        )

    @application.get("/health", tags=["Sistema"])
    async def health_check():
        return {"status": "ok"}

    application.include_router(api_router, prefix=settings.API_V1_STR)
    return application

app = create_application()

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logger import logger
from app.routers import api_router


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        description="Core Financiero (Local Desktop Edition)",
    )

    from fastapi import Request

    # Pilar 6 y 3: Manejo Global de Errores (JSON estructurado, sin stack traces)
    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning(f"Rechazo de Capa Anti-Corrupción (422): {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "Error en el formato de los datos enviados.",
                "code": "ERR_VALIDATION_422",
                "details": jsonable_encoder(exc.errors())
            },
        )

    @application.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # Pilar 7: Logs estructurados con stack trace, pero respuesta limpia al frontend
        logger.error("Fallo interno no controlado", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Ha ocurrido un error interno en el sistema. Contacte soporte.",
                "code": "ERR_INTERNAL_500"
            },
        )

    @application.get("/health", tags=["Sistema"])
    async def health_check() -> dict:
        return {"status": "ok"}

    application.include_router(api_router, prefix=settings.API_V1_STR)
    return application

app = create_application()

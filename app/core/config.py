import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "Automatizador de Finanzas Personales"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Variables de PostgreSQL eliminadas. Ahora usamos SQLite local para portabilidad.
    SQLITE_DB_NAME: str = Field(default="mis_finanzas.db", validation_alias="SQLITE_DB_NAME")

    SECRET_KEY: str = Field(default="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7", validation_alias="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def async_database_url(self) -> str:
        # aiolite se conecta a archivos locales
        return f"sqlite+aiosqlite:///{self.SQLITE_DB_NAME}"

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()

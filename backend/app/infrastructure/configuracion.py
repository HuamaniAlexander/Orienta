from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracion(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)
    url_base_datos: str = Field(
        default="postgresql+psycopg://orienta:change-me-local@localhost:5432/orienta",
        validation_alias=AliasChoices("url_base_datos", "database_url", "DATABASE_URL"),
    )
    modo_datos: Literal["postgres", "demo"] = Field(
        default="postgres", validation_alias=AliasChoices("modo_datos", "data_mode", "DATA_MODE")
    )
    ruta_catalogo_json: Path = Field(
        default=Path(__file__).resolve().parents[2] / "data" / "catalogo_lima_norte_2026.json",
        validation_alias=AliasChoices("ruta_catalogo_json", "demo_path", "DEMO_PATH"),
    )
    directorio_modelos: Path = Field(
        default=Path(__file__).resolve().parents[2] / "models",
        validation_alias=AliasChoices("directorio_modelos", "model_directory", "MODEL_DIRECTORY"),
    )
    origenes_cors: list[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        validation_alias=AliasChoices("origenes_cors", "cors_origins", "CORS_ORIGINS"),
    )

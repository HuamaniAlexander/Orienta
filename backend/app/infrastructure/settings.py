from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg://orienta:change-me-local@localhost:5432/orienta"
    data_mode: Literal["postgres", "demo"] = "postgres"
    demo_path: Path = Path(__file__).resolve().parents[2] / "data" / "catalog.json"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

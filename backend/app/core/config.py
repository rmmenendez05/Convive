"""Configuración leída de variables de entorno."""

import os
from dataclasses import dataclass, field

DEV_SECRET = "dev-secret-cambiar-en-produccion"


def _lista(valor: str) -> list[str]:
    return [v.strip() for v in valor.split(",") if v.strip()]


@dataclass(frozen=True)
class Settings:
    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./convive.db")
    )
    jwt_secret: str = field(default_factory=lambda: os.getenv("JWT_SECRET", DEV_SECRET))
    jwt_expires_hours: int = field(
        default_factory=lambda: int(os.getenv("JWT_EXPIRES_HOURS", "24"))
    )
    cors_origins: list[str] = field(
        default_factory=lambda: _lista(os.getenv("CORS_ORIGINS", ""))
    )


settings = Settings()

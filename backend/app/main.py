"""Punto de entrada de la API de Convive."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import registrar_manejadores
from app.routers import auth, avisos, pisos


def crear_app() -> FastAPI:
    app = FastAPI(title="Convive API", version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    registrar_manejadores(app)
    for router in (auth.router, pisos.router, avisos.router):
        app.include_router(router, prefix="/api")
    return app


app = crear_app()

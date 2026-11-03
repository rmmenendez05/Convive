"""Excepción de la aplicación y manejadores que producen el formato único de error."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.i18n import idioma_de, mensaje

logger = logging.getLogger("convive")

CODIGOS_HTTP = {
    401: "no_autenticado",
    403: "permiso_denegado",
    404: "no_encontrado",
    405: "metodo_no_permitido",
}


class AppError(Exception):
    def __init__(self, status: int, code: str):
        super().__init__(code)
        self.status = status
        self.code = code


def respuesta_error(
    request: Request, status: int, code: str, details: list | None = None
) -> JSONResponse:
    cuerpo: dict = {"code": code, "message": mensaje(code, idioma_de(request.headers.get("accept-language")))}
    if details:
        cuerpo["details"] = details
    headers = {"WWW-Authenticate": "Bearer"} if status == 401 else None
    return JSONResponse(status_code=status, content={"error": cuerpo}, headers=headers)


def _detalles_validacion(exc: RequestValidationError) -> list[dict]:
    detalles = []
    for err in exc.errors():
        loc = [str(p) for p in err.get("loc", ()) if p not in ("body", "query", "path")]
        detalles.append({"field": ".".join(loc) or None, "code": err.get("type", "invalid")})
    return detalles


def registrar_manejadores(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(request: Request, exc: AppError):
        return respuesta_error(request, exc.status, exc.code)

    @app.exception_handler(RequestValidationError)
    async def _validacion(request: Request, exc: RequestValidationError):
        return respuesta_error(request, 400, "datos_invalidos", _detalles_validacion(exc))

    @app.exception_handler(StarletteHTTPException)
    async def _http(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 400:
            return respuesta_error(request, 400, "datos_invalidos")
        code = CODIGOS_HTTP.get(exc.status_code, "error_interno")
        return respuesta_error(request, exc.status_code, code)

    @app.exception_handler(Exception)
    async def _inesperado(request: Request, exc: Exception):
        logger.exception("Error no controlado", exc_info=exc)
        return respuesta_error(request, 500, "error_interno")

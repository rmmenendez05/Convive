"""Dependencias de FastAPI: sesión de BD, usuario autenticado y membresía."""

from collections.abc import Iterator

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.errors import AppError
from app.core.security import leer_token
from app.models import Miembro, Usuario


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _token_de(request: Request) -> str | None:
    cabecera = request.headers.get("authorization", "")
    esquema, _, token = cabecera.partition(" ")
    if esquema.lower() != "bearer" or not token.strip():
        return None
    return token.strip()


def get_usuario_actual(request: Request, db: Session = Depends(get_db)) -> Usuario:
    token = _token_de(request)
    usuario_id = leer_token(token) if token else None
    usuario = db.get(Usuario, usuario_id) if usuario_id is not None else None
    if usuario is None:
        raise AppError(401, "no_autenticado")
    return usuario


def get_miembro_actual(usuario: Usuario = Depends(get_usuario_actual)) -> Miembro:
    if usuario.membresia is None:
        raise AppError(404, "sin_piso")
    return usuario.membresia

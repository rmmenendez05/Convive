"""Registro, inicio de sesión y datos del usuario actual."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import HASH_FICTICIO, crear_token, hash_password, verificar_password
from app.models import Usuario
from app.schemas.auth import LoginIn, RegistroIn, TokenOut, UsuarioOut, YoOut


def normalizar_email(email: str) -> str:
    return email.strip().lower()


def _buscar_por_email(db: Session, email: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.email == normalizar_email(email)))


def registrar(db: Session, datos: RegistroIn) -> Usuario:
    if _buscar_por_email(db, datos.email) is not None:
        raise AppError(409, "email_ya_registrado")
    usuario = Usuario(
        email=normalizar_email(datos.email),
        password_hash=hash_password(datos.password),
        nombre=datos.nombre,
    )
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError:
        # Otro registro simultáneo con el mismo email ganó la carrera.
        db.rollback()
        raise AppError(409, "email_ya_registrado") from None
    return usuario


def iniciar_sesion(db: Session, datos: LoginIn) -> TokenOut:
    usuario = _buscar_por_email(db, datos.email)
    # Se verifica siempre un hash para no revelar por tiempo si el email existe.
    hash_a_comprobar = usuario.password_hash if usuario else HASH_FICTICIO
    password_ok = verificar_password(datos.password, hash_a_comprobar)
    if usuario is None or not password_ok:
        raise AppError(401, "credenciales_invalidas")
    token, expira = crear_token(usuario.id)
    return TokenOut(token=token, expira_en=expira, usuario=usuario_out(usuario))


def usuario_out(usuario: Usuario) -> UsuarioOut:
    return UsuarioOut(id=usuario.id, email=usuario.email, nombre=usuario.nombre)


def yo(usuario: Usuario) -> YoOut:
    membresia = usuario.membresia
    return YoOut(
        **usuario_out(usuario).model_dump(),
        piso_id=membresia.piso_id if membresia else None,
        rol=membresia.rol if membresia else None,
    )

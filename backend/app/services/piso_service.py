"""Pisos y membresía: crear, unirse, ver, expulsar, abandonar y regenerar código."""

import re
import secrets
import string

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import ROL_ADMIN, ROL_MIEMBRO, Aviso, Miembro, Piso, Usuario
from app.schemas.piso import CodigoOut, MiembroOut, PisoIn, PisoOut

ALFABETO_CODIGO = string.ascii_uppercase + string.digits
LONGITUD_CODIGO = 8
PATRON_CODIGO = re.compile(r"^[A-Z0-9]{8}$")
MAX_INTENTOS_CODIGO = 5


def generar_codigo(db: Session) -> str:
    for _ in range(MAX_INTENTOS_CODIGO):
        codigo = "".join(secrets.choice(ALFABETO_CODIGO) for _ in range(LONGITUD_CODIGO))
        if db.scalar(select(Piso.id).where(Piso.codigo_invitacion == codigo)) is None:
            return codigo
    raise RuntimeError("No se pudo generar un código de invitación único")


def _comprobar_sin_piso(usuario: Usuario) -> None:
    if usuario.membresia is not None:
        raise AppError(409, "ya_tiene_piso")


def _guardar_membresia(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        # El usuario se unió a otro piso en una petición simultánea.
        db.rollback()
        raise AppError(409, "ya_tiene_piso") from None


def crear_piso(db: Session, usuario: Usuario, datos: PisoIn) -> PisoOut:
    _comprobar_sin_piso(usuario)
    piso = Piso(nombre=datos.nombre, direccion=datos.direccion, codigo_invitacion=generar_codigo(db))
    db.add(piso)
    db.flush()
    db.add(Miembro(usuario_id=usuario.id, piso_id=piso.id, rol=ROL_ADMIN))
    _guardar_membresia(db)
    db.refresh(usuario)
    return vista_piso(usuario.membresia)


def normalizar_codigo(codigo: str) -> str:
    return codigo.strip().upper()


def unirse(db: Session, usuario: Usuario, codigo: str) -> PisoOut:
    _comprobar_sin_piso(usuario)
    codigo = normalizar_codigo(codigo)
    piso = None
    if PATRON_CODIGO.match(codigo):
        piso = db.scalar(select(Piso).where(Piso.codigo_invitacion == codigo))
    if piso is None:
        raise AppError(404, "codigo_invalido")
    db.add(Miembro(usuario_id=usuario.id, piso_id=piso.id, rol=ROL_MIEMBRO))
    _guardar_membresia(db)
    db.refresh(usuario)
    return vista_piso(usuario.membresia)


def vista_piso(miembro: Miembro) -> PisoOut:
    piso = miembro.piso
    datos = {
        "id": piso.id,
        "nombre": piso.nombre,
        "direccion": piso.direccion,
        "miembros": [
            MiembroOut(usuario_id=m.usuario_id, nombre=m.usuario.nombre, rol=m.rol, unido_en=m.unido_en)
            for m in piso.miembros
        ],
    }
    if miembro.es_admin:
        datos["codigo_invitacion"] = piso.codigo_invitacion
    return PisoOut(**datos)


def _exigir_admin(miembro: Miembro) -> None:
    if not miembro.es_admin:
        raise AppError(403, "permiso_denegado")


def _sacar_del_piso(db: Session, miembro: Miembro) -> None:
    """Borra los avisos del miembro, su membresía y, si era admin, traspasa el rol o borra el piso."""
    piso = miembro.piso
    era_admin = miembro.es_admin
    db.execute(delete(Aviso).where(Aviso.piso_id == piso.id, Aviso.autor_id == miembro.usuario_id))
    piso.miembros.remove(miembro)
    db.delete(miembro)
    db.flush()
    if not piso.miembros:
        db.delete(piso)
    elif era_admin:
        piso.miembros[0].rol = ROL_ADMIN  # el más antiguo (orden por unido_en, usuario_id)
    db.commit()


def expulsar(db: Session, admin: Miembro, usuario_id: int) -> None:
    _exigir_admin(admin)
    if usuario_id == admin.usuario_id:
        raise AppError(400, "no_puede_expulsarse")
    objetivo = db.get(Miembro, usuario_id)
    if objetivo is None or objetivo.piso_id != admin.piso_id:
        raise AppError(404, "miembro_no_encontrado")
    _sacar_del_piso(db, objetivo)


def abandonar(db: Session, miembro: Miembro) -> None:
    _sacar_del_piso(db, miembro)


def regenerar_codigo(db: Session, admin: Miembro) -> CodigoOut:
    _exigir_admin(admin)
    admin.piso.codigo_invitacion = generar_codigo(db)
    db.commit()
    return CodigoOut(codigo_invitacion=admin.piso.codigo_invitacion)

"""Tablón de avisos: publicar, listar y borrar."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import Aviso, Miembro
from app.schemas.aviso import AutorOut, AvisoIn, AvisoOut


def aviso_out(aviso: Aviso) -> AvisoOut:
    return AvisoOut(
        id=aviso.id,
        texto=aviso.texto,
        autor=AutorOut(id=aviso.autor.id, nombre=aviso.autor.nombre),
        creado_en=aviso.creado_en,
    )


def publicar(db: Session, miembro: Miembro, datos: AvisoIn) -> AvisoOut:
    aviso = Aviso(piso_id=miembro.piso_id, autor_id=miembro.usuario_id, texto=datos.texto)
    db.add(aviso)
    db.commit()
    db.refresh(aviso)
    return aviso_out(aviso)


def listar(db: Session, miembro: Miembro) -> list[AvisoOut]:
    avisos = db.scalars(
        select(Aviso)
        .where(Aviso.piso_id == miembro.piso_id)
        .order_by(Aviso.creado_en.desc(), Aviso.id.desc())
    )
    return [aviso_out(a) for a in avisos]


def borrar(db: Session, miembro: Miembro, aviso_id: int) -> None:
    aviso = db.get(Aviso, aviso_id)
    # Un aviso de otro piso se trata como inexistente para no revelar nada.
    if aviso is None or aviso.piso_id != miembro.piso_id:
        raise AppError(404, "aviso_no_encontrado")
    if aviso.autor_id != miembro.usuario_id and not miembro.es_admin:
        raise AppError(403, "permiso_denegado")
    db.delete(aviso)
    db.commit()

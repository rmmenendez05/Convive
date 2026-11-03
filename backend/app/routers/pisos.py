from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.deps import get_db, get_miembro_actual, get_usuario_actual
from app.models import Miembro, Usuario
from app.schemas.piso import CodigoOut, PisoIn, PisoOut, UnirseIn
from app.services import piso_service

router = APIRouter(prefix="/pisos", tags=["pisos"])


@router.post("", status_code=201, response_model=PisoOut, response_model_exclude_unset=True)
def crear(datos: PisoIn, usuario: Usuario = Depends(get_usuario_actual), db: Session = Depends(get_db)):
    return piso_service.crear_piso(db, usuario, datos)


@router.post("/unirse", response_model=PisoOut, response_model_exclude_unset=True)
def unirse(datos: UnirseIn, usuario: Usuario = Depends(get_usuario_actual), db: Session = Depends(get_db)):
    return piso_service.unirse(db, usuario, datos.codigo)


@router.get("/mio", response_model=PisoOut, response_model_exclude_unset=True)
def ver(miembro: Miembro = Depends(get_miembro_actual)):
    return piso_service.vista_piso(miembro)


@router.delete("/mio/miembros/{usuario_id}", status_code=204)
def expulsar(usuario_id: int, miembro: Miembro = Depends(get_miembro_actual), db: Session = Depends(get_db)):
    piso_service.expulsar(db, miembro, usuario_id)
    return Response(status_code=204)


@router.post("/mio/abandonar", status_code=204)
def abandonar(miembro: Miembro = Depends(get_miembro_actual), db: Session = Depends(get_db)):
    piso_service.abandonar(db, miembro)
    return Response(status_code=204)


@router.post("/mio/codigo", response_model=CodigoOut)
def regenerar_codigo(miembro: Miembro = Depends(get_miembro_actual), db: Session = Depends(get_db)):
    return piso_service.regenerar_codigo(db, miembro)

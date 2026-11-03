from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.deps import get_db, get_miembro_actual
from app.models import Miembro
from app.schemas.aviso import AvisoIn, AvisoOut
from app.services import aviso_service

router = APIRouter(prefix="/avisos", tags=["avisos"])


@router.post("", status_code=201, response_model=AvisoOut)
def publicar(datos: AvisoIn, miembro: Miembro = Depends(get_miembro_actual), db: Session = Depends(get_db)):
    return aviso_service.publicar(db, miembro, datos)


@router.get("", response_model=list[AvisoOut])
def listar(miembro: Miembro = Depends(get_miembro_actual), db: Session = Depends(get_db)):
    return aviso_service.listar(db, miembro)


@router.delete("/{aviso_id}", status_code=204)
def borrar(aviso_id: int, miembro: Miembro = Depends(get_miembro_actual), db: Session = Depends(get_db)):
    aviso_service.borrar(db, miembro, aviso_id)
    return Response(status_code=204)

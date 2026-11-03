from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db, get_usuario_actual
from app.models import Usuario
from app.schemas.auth import LoginIn, RegistroIn, TokenOut, UsuarioOut, YoOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registro", status_code=201, response_model=UsuarioOut)
def registro(datos: RegistroIn, db: Session = Depends(get_db)):
    return auth_service.usuario_out(auth_service.registrar(db, datos))


@router.post("/login", response_model=TokenOut)
def login(datos: LoginIn, db: Session = Depends(get_db)):
    return auth_service.iniciar_sesion(db, datos)


@router.get("/yo", response_model=YoOut)
def yo(usuario: Usuario = Depends(get_usuario_actual)):
    return auth_service.yo(usuario)

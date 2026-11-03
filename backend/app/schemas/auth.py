from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, EmailStr, StringConstraints

Nombre = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=40)]
Password = Annotated[str, StringConstraints(min_length=8, max_length=128)]


class RegistroIn(BaseModel):
    email: EmailStr
    password: Password
    nombre: Nombre


class LoginIn(BaseModel):
    email: Annotated[str, StringConstraints(max_length=254)]
    password: Annotated[str, StringConstraints(max_length=128)]


class UsuarioOut(BaseModel):
    id: int
    email: str
    nombre: str


class TokenOut(BaseModel):
    token: str
    expira_en: datetime
    usuario: UsuarioOut


class YoOut(UsuarioOut):
    piso_id: int | None
    rol: Literal["admin", "miembro"] | None

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, StringConstraints, field_validator

NombrePiso = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=60)]


class PisoIn(BaseModel):
    nombre: NombrePiso
    direccion: Annotated[str, StringConstraints(strip_whitespace=True, max_length=200)] | None = None

    @field_validator("direccion")
    @classmethod
    def vacia_a_none(cls, valor: str | None) -> str | None:
        return valor or None


class UnirseIn(BaseModel):
    codigo: Annotated[str, StringConstraints(max_length=50)]


class MiembroOut(BaseModel):
    usuario_id: int
    nombre: str
    rol: Literal["admin", "miembro"]
    unido_en: datetime


class PisoOut(BaseModel):
    """`codigo_invitacion` solo se incluye para el administrador (la clave se omite)."""

    id: int
    nombre: str
    direccion: str | None
    codigo_invitacion: str | None = None
    miembros: list[MiembroOut]


class CodigoOut(BaseModel):
    codigo_invitacion: str

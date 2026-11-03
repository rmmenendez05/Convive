from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, StringConstraints

TextoAviso = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=280)]


class AvisoIn(BaseModel):
    texto: TextoAviso


class AutorOut(BaseModel):
    id: int
    nombre: str


class AvisoOut(BaseModel):
    id: int
    texto: str
    autor: AutorOut
    creado_en: datetime

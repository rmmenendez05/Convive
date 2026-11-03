from datetime import datetime

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.tipos import FechaUTC, ahora_utc


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre: Mapped[str] = mapped_column(String(40), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(FechaUTC, default=ahora_utc, nullable=False)

    membresia: Mapped["Miembro | None"] = relationship(  # noqa: F821
        back_populates="usuario", uselist=False
    )

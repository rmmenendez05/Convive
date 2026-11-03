from datetime import datetime

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.tipos import FechaUTC, ahora_utc


class Piso(Base):
    __tablename__ = "pisos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(60), nullable=False)
    direccion: Mapped[str | None] = mapped_column(String(200), nullable=True)
    codigo_invitacion: Mapped[str] = mapped_column(String(8), unique=True, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(FechaUTC, default=ahora_utc, nullable=False)

    miembros: Mapped[list["Miembro"]] = relationship(  # noqa: F821
        back_populates="piso",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="(Miembro.unido_en, Miembro.usuario_id)",
    )
    avisos: Mapped[list["Aviso"]] = relationship(  # noqa: F821
        back_populates="piso", cascade="all, delete-orphan", passive_deletes=True
    )

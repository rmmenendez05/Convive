from datetime import datetime

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.tipos import FechaUTC, ahora_utc


class Aviso(Base):
    __tablename__ = "avisos"
    __table_args__ = (Index("ix_avisos_piso_fecha", "piso_id", "creado_en"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    piso_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pisos.id", ondelete="CASCADE"), nullable=False
    )
    autor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    texto: Mapped[str] = mapped_column(String(280), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(FechaUTC, default=ahora_utc, nullable=False)

    piso: Mapped["Piso"] = relationship(back_populates="avisos")  # noqa: F821
    autor: Mapped["Usuario"] = relationship()  # noqa: F821

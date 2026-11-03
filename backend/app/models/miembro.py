from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.tipos import FechaUTC, ahora_utc

ROL_ADMIN = "admin"
ROL_MIEMBRO = "miembro"


class Miembro(Base):
    __tablename__ = "miembros"
    __table_args__ = (CheckConstraint("rol IN ('admin', 'miembro')", name="ck_miembros_rol"),)

    # Clave primaria = usuario: garantiza un piso por usuario.
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True
    )
    piso_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pisos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rol: Mapped[str] = mapped_column(String(10), nullable=False, default=ROL_MIEMBRO)
    unido_en: Mapped[datetime] = mapped_column(FechaUTC, default=ahora_utc, nullable=False)

    usuario: Mapped["Usuario"] = relationship(back_populates="membresia")  # noqa: F821
    piso: Mapped["Piso"] = relationship(back_populates="miembros")  # noqa: F821

    @property
    def es_admin(self) -> bool:
        return self.rol == ROL_ADMIN

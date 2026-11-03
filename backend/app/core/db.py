"""Motor de base de datos, sesiones y clase base de los modelos."""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def crear_engine(url: str, **kwargs) -> Engine:
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=connect_args, **kwargs)
    if url.startswith("sqlite"):
        event.listen(engine, "connect", _activar_claves_foraneas)
    return engine


def _activar_claves_foraneas(conexion, _registro) -> None:
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


engine = crear_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

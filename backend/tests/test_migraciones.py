"""La migración de Alembic crea el mismo esquema que los modelos."""

from pathlib import Path

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import inspect

from app.core.db import Base, crear_engine

BACKEND = Path(__file__).resolve().parent.parent


def test_upgrade_head_crea_el_esquema_de_los_modelos(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'migr.db'}"
    monkeypatch.setenv("DATABASE_URL", url)
    config = Config(str(BACKEND / "alembic.ini"))
    config.attributes["configure_logger"] = False
    command.upgrade(config, "head")

    engine = crear_engine(url)
    try:
        tablas = set(inspect(engine).get_table_names())
        assert {"usuarios", "pisos", "miembros", "avisos"} <= tablas
        with engine.connect() as conn:
            diferencias = compare_metadata(MigrationContext.configure(conn), Base.metadata)
        assert diferencias == []
    finally:
        engine.dispose()

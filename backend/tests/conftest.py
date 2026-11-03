import itertools

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import Base, crear_engine
from app.deps import get_db
from app.main import app

PASSWORD = "secreto123"
_contador = itertools.count(1)


@pytest.fixture
def db_session_factory():
    engine = crear_engine("sqlite://", poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    yield factory
    engine.dispose()


@pytest.fixture
def client(db_session_factory):
    def _get_db():
        db = db_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def crear_usuario(client):
    """Registra un usuario y devuelve {id, email, nombre, token, headers}."""

    def _crear(nombre: str | None = None, email: str | None = None, password: str = PASSWORD):
        n = next(_contador)
        nombre = nombre or f"Usuario{n}"
        email = email or f"usuario{n}@test.com"
        r = client.post("/api/auth/registro", json={"email": email, "password": password, "nombre": nombre})
        assert r.status_code == 201, r.text
        r = client.post("/api/auth/login", json={"email": email, "password": password})
        assert r.status_code == 200, r.text
        token = r.json()["token"]
        return {**r.json()["usuario"], "token": token, "headers": auth(token)}

    return _crear


@pytest.fixture
def crear_piso_con_miembros(client, crear_usuario):
    """Crea un piso con un admin y `n_miembros` miembros. Devuelve (piso, admin, [miembros])."""

    def _crear(n_miembros: int = 0, nombre: str = "Piso de prueba"):
        admin = crear_usuario()
        r = client.post("/api/pisos", json={"nombre": nombre}, headers=admin["headers"])
        assert r.status_code == 201, r.text
        piso = r.json()
        miembros = []
        for _ in range(n_miembros):
            m = crear_usuario()
            r = client.post("/api/pisos/unirse", json={"codigo": piso["codigo_invitacion"]}, headers=m["headers"])
            assert r.status_code == 200, r.text
            miembros.append(m)
        return piso, admin, miembros

    return _crear


def assert_error(respuesta, status: int, code: str) -> None:
    assert respuesta.status_code == status, respuesta.text
    cuerpo = respuesta.json()
    assert set(cuerpo) == {"error"}
    assert cuerpo["error"]["code"] == code
    assert isinstance(cuerpo["error"]["message"], str) and cuerpo["error"]["message"]

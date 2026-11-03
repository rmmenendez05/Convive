"""US1 · Registro (HU-01) e inicio de sesión (HU-02)."""

import pytest
from sqlalchemy import select

from app.models import Usuario
from app.services import auth_service
from tests.conftest import PASSWORD, assert_error


def registrar(client, email="ana@test.com", password=PASSWORD, nombre="Ana"):
    return client.post("/api/auth/registro", json={"email": email, "password": password, "nombre": nombre})


# --- Registro -------------------------------------------------------------

def test_registro_correcto(client):
    r = registrar(client)
    assert r.status_code == 201
    assert r.json() == {"id": r.json()["id"], "email": "ana@test.com", "nombre": "Ana"}


def test_registro_guarda_email_en_minusculas(client):
    assert registrar(client, email="Ana@Test.COM").json()["email"] == "ana@test.com"


def test_registro_email_duplicado_409(client):
    registrar(client)
    assert_error(registrar(client, nombre="Otra"), 409, "email_ya_registrado")


def test_registro_email_duplicado_con_mayusculas_409(client):
    registrar(client)
    assert_error(registrar(client, email="ANA@test.com"), 409, "email_ya_registrado")


@pytest.mark.parametrize("email", ["sin-arroba", "a@", "@b.com", ""])
def test_registro_email_mal_formado_400(client, email):
    assert_error(registrar(client, email=email), 400, "datos_invalidos")


def test_registro_password_corta_400(client):
    assert_error(registrar(client, password="1234567"), 400, "datos_invalidos")


def test_registro_password_de_8_es_valida(client):
    assert registrar(client, password="12345678").status_code == 201


@pytest.mark.parametrize("nombre", ["", "   ", "x" * 41])
def test_registro_nombre_invalido_400(client, nombre):
    assert_error(registrar(client, nombre=nombre), 400, "datos_invalidos")


def test_registro_sin_nombre_400(client):
    r = client.post("/api/auth/registro", json={"email": "a@test.com", "password": PASSWORD})
    assert_error(r, 400, "datos_invalidos")


def test_registro_nombre_de_40_es_valido(client):
    assert registrar(client, nombre="x" * 40).status_code == 201


def test_registro_no_guarda_la_password_en_claro(client, db_session_factory):
    registrar(client)
    with db_session_factory() as db:
        usuario = db.scalar(select(Usuario))
    assert PASSWORD not in usuario.password_hash
    assert usuario.password_hash.startswith("$argon2")


def test_registro_simultaneo_mismo_email_devuelve_409(client, monkeypatch):
    """Si dos registros pasan la comprobación a la vez, la restricción UNIQUE da 409, no 500."""
    registrar(client)
    monkeypatch.setattr(auth_service, "_buscar_por_email", lambda db, email: None)
    assert_error(registrar(client), 409, "email_ya_registrado")


# --- Login ----------------------------------------------------------------

def test_login_correcto_devuelve_token(client):
    registrar(client)
    r = client.post("/api/auth/login", json={"email": "ana@test.com", "password": PASSWORD})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["token"]
    assert cuerpo["expira_en"]
    assert cuerpo["usuario"]["nombre"] == "Ana"


def test_login_no_distingue_mayusculas_en_email(client):
    registrar(client)
    r = client.post("/api/auth/login", json={"email": "ANA@test.com", "password": PASSWORD})
    assert r.status_code == 200


def test_login_password_incorrecta_y_email_inexistente_dan_el_mismo_error(client):
    registrar(client)
    mal_password = client.post("/api/auth/login", json={"email": "ana@test.com", "password": "otra-cosa"})
    no_existe = client.post("/api/auth/login", json={"email": "nadie@test.com", "password": PASSWORD})
    assert_error(mal_password, 401, "credenciales_invalidas")
    assert_error(no_existe, 401, "credenciales_invalidas")
    assert mal_password.json() == no_existe.json()


def test_login_sin_campos_400(client):
    assert_error(client.post("/api/auth/login", json={}), 400, "datos_invalidos")


# --- Usuario actual -------------------------------------------------------

def test_yo_sin_piso(client, crear_usuario):
    u = crear_usuario(nombre="Luis")
    r = client.get("/api/auth/yo", headers=u["headers"])
    assert r.status_code == 200
    assert r.json() == {"id": u["id"], "email": u["email"], "nombre": "Luis", "piso_id": None, "rol": None}


def test_yo_con_piso(client, crear_piso_con_miembros):
    piso, admin, [miembro] = crear_piso_con_miembros(1)
    assert client.get("/api/auth/yo", headers=admin["headers"]).json()["rol"] == "admin"
    yo = client.get("/api/auth/yo", headers=miembro["headers"]).json()
    assert yo["piso_id"] == piso["id"]
    assert yo["rol"] == "miembro"

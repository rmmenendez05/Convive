"""Formato único de error, autenticación e idioma de los mensajes."""

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.core.errors import registrar_manejadores
from app.core.security import crear_token
from app.main import crear_app
from tests.conftest import assert_error, auth


def test_validacion_devuelve_400_con_formato_unico(client):
    r = client.post("/api/auth/registro", json={"email": "no-es-email", "password": "x"})
    assert_error(r, 400, "datos_invalidos")
    campos = {d["field"] for d in r.json()["error"]["details"]}
    assert {"email", "password", "nombre"} <= campos


def test_json_mal_formado_devuelve_400(client):
    r = client.post("/api/auth/login", content="{no json", headers={"Content-Type": "application/json"})
    assert_error(r, 400, "datos_invalidos")


def test_sin_token_devuelve_401(client):
    assert_error(client.get("/api/auth/yo"), 401, "no_autenticado")
    assert_error(client.get("/api/pisos/mio"), 401, "no_autenticado")
    assert_error(client.get("/api/avisos"), 401, "no_autenticado")


def test_token_manipulado_devuelve_401(client, crear_usuario):
    u = crear_usuario()
    assert_error(client.get("/api/auth/yo", headers=auth(u["token"] + "x")), 401, "no_autenticado")
    assert_error(client.get("/api/auth/yo", headers={"Authorization": "Basic abc"}), 401, "no_autenticado")


def test_token_caducado_devuelve_401(client, crear_usuario):
    u = crear_usuario()
    hace_25h = datetime.now(timezone.utc) - timedelta(hours=25)
    token, _ = crear_token(u["id"], ahora=hace_25h)
    assert_error(client.get("/api/auth/yo", headers=auth(token)), 401, "no_autenticado")


def test_token_dura_24_horas(client, crear_usuario):
    u = crear_usuario()
    hace_23h = datetime.now(timezone.utc) - timedelta(hours=23)
    token, expira = crear_token(u["id"], ahora=hace_23h)
    assert client.get("/api/auth/yo", headers=auth(token)).status_code == 200
    assert expira - hace_23h == timedelta(hours=24)


def test_token_de_usuario_inexistente_devuelve_401(client):
    token, _ = crear_token(9999)
    assert_error(client.get("/api/auth/yo", headers=auth(token)), 401, "no_autenticado")


def test_mensaje_en_ingles_con_accept_language(client):
    r = client.get("/api/auth/yo", headers={"Accept-Language": "en-GB,en;q=0.9"})
    assert r.json()["error"]["message"] == "You need to sign in"


def test_mensaje_en_espanol_por_defecto(client):
    assert client.get("/api/auth/yo").json()["error"]["message"] == "Tienes que iniciar sesión"
    r = client.get("/api/auth/yo", headers={"Accept-Language": "fr"})
    assert r.json()["error"]["message"] == "Tienes que iniciar sesión"


def test_ruta_inexistente_devuelve_404_con_formato_unico(client):
    assert_error(client.get("/api/no-existe"), 404, "no_encontrado")


def test_metodo_no_permitido_con_formato_unico(client):
    assert_error(client.put("/api/auth/login"), 405, "metodo_no_permitido")


def test_error_inesperado_devuelve_500_con_formato_unico():
    app = crear_app()
    registrar_manejadores(app)

    @app.get("/api/explota")
    def _explota():
        raise RuntimeError("boom")

    r = TestClient(app, raise_server_exceptions=False).get("/api/explota")
    assert_error(r, 500, "error_interno")

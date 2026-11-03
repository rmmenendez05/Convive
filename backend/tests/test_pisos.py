"""US2 · Crear piso (HU-03) y unirse (HU-04). US3 · Ver piso (HU-05)."""

import re

import pytest

from tests.conftest import assert_error

PATRON = re.compile(r"^[A-Z0-9]{8}$")


# --- Crear piso -----------------------------------------------------------

def test_crear_piso_correcto(client, crear_usuario):
    u = crear_usuario(nombre="Ana")
    r = client.post("/api/pisos", json={"nombre": "Calle Mayor 3", "direccion": "C/ Mayor 3"}, headers=u["headers"])
    assert r.status_code == 201
    piso = r.json()
    assert piso["nombre"] == "Calle Mayor 3"
    assert piso["direccion"] == "C/ Mayor 3"
    assert PATRON.match(piso["codigo_invitacion"])
    assert [(m["usuario_id"], m["rol"]) for m in piso["miembros"]] == [(u["id"], "admin")]


def test_crear_piso_sin_direccion(client, crear_usuario):
    u = crear_usuario()
    r = client.post("/api/pisos", json={"nombre": "Piso", "direccion": "  "}, headers=u["headers"])
    assert r.status_code == 201
    assert r.json()["direccion"] is None


@pytest.mark.parametrize("nombre", ["", "   ", "x" * 61])
def test_crear_piso_nombre_invalido_400(client, crear_usuario, nombre):
    u = crear_usuario()
    assert_error(client.post("/api/pisos", json={"nombre": nombre}, headers=u["headers"]), 400, "datos_invalidos")


def test_crear_piso_nombre_de_60_es_valido(client, crear_usuario):
    u = crear_usuario()
    assert client.post("/api/pisos", json={"nombre": "x" * 60}, headers=u["headers"]).status_code == 201


def test_crear_piso_direccion_larga_400(client, crear_usuario):
    u = crear_usuario()
    r = client.post("/api/pisos", json={"nombre": "Piso", "direccion": "x" * 201}, headers=u["headers"])
    assert_error(r, 400, "datos_invalidos")


def test_crear_piso_teniendo_piso_409(client, crear_piso_con_miembros):
    _, admin, [miembro] = crear_piso_con_miembros(1)
    assert_error(client.post("/api/pisos", json={"nombre": "Otro"}, headers=admin["headers"]), 409, "ya_tiene_piso")
    assert_error(client.post("/api/pisos", json={"nombre": "Otro"}, headers=miembro["headers"]), 409, "ya_tiene_piso")


def test_crear_piso_sin_token_401(client):
    assert_error(client.post("/api/pisos", json={"nombre": "Piso"}), 401, "no_autenticado")


def test_codigos_de_pisos_distintos_son_diferentes(crear_piso_con_miembros):
    codigos = {crear_piso_con_miembros()[0]["codigo_invitacion"] for _ in range(5)}
    assert len(codigos) == 5


# --- Unirse ---------------------------------------------------------------

def test_unirse_con_codigo_valido(client, crear_piso_con_miembros, crear_usuario):
    piso, admin, _ = crear_piso_con_miembros()
    luis = crear_usuario(nombre="Luis")
    r = client.post("/api/pisos/unirse", json={"codigo": piso["codigo_invitacion"]}, headers=luis["headers"])
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["id"] == piso["id"]
    assert "codigo_invitacion" not in cuerpo
    roles = {m["usuario_id"]: m["rol"] for m in cuerpo["miembros"]}
    assert roles == {admin["id"]: "admin", luis["id"]: "miembro"}


def test_unirse_con_codigo_en_minusculas_y_espacios(client, crear_piso_con_miembros, crear_usuario):
    piso, _, _ = crear_piso_con_miembros()
    u = crear_usuario()
    codigo = f"  {piso['codigo_invitacion'].lower()} "
    assert client.post("/api/pisos/unirse", json={"codigo": codigo}, headers=u["headers"]).status_code == 200


@pytest.mark.parametrize("codigo", ["ZZZZZZZZ", "corto", "", "!!!!!!!!"])
def test_unirse_codigo_inexistente_404(client, crear_usuario, codigo):
    u = crear_usuario()
    assert_error(client.post("/api/pisos/unirse", json={"codigo": codigo}, headers=u["headers"]), 404, "codigo_invalido")


def test_unirse_teniendo_piso_409(client, crear_piso_con_miembros):
    piso_a, admin_a, _ = crear_piso_con_miembros()
    piso_b, _, _ = crear_piso_con_miembros()
    r = client.post("/api/pisos/unirse", json={"codigo": piso_b["codigo_invitacion"]}, headers=admin_a["headers"])
    assert_error(r, 409, "ya_tiene_piso")
    r = client.post("/api/pisos/unirse", json={"codigo": piso_a["codigo_invitacion"]}, headers=admin_a["headers"])
    assert_error(r, 409, "ya_tiene_piso")


def test_unirse_sin_token_401(client):
    assert_error(client.post("/api/pisos/unirse", json={"codigo": "ABCDEFGH"}), 401, "no_autenticado")


# --- Ver piso -------------------------------------------------------------

def test_admin_ve_el_codigo(client, crear_piso_con_miembros):
    piso, admin, _ = crear_piso_con_miembros(1)
    r = client.get("/api/pisos/mio", headers=admin["headers"])
    assert r.status_code == 200
    assert r.json()["codigo_invitacion"] == piso["codigo_invitacion"]


def test_miembro_no_ve_el_codigo(client, crear_piso_con_miembros):
    _, _, [miembro] = crear_piso_con_miembros(1)
    cuerpo = client.get("/api/pisos/mio", headers=miembro["headers"]).json()
    assert "codigo_invitacion" not in cuerpo
    assert cuerpo["nombre"] == "Piso de prueba"
    assert "direccion" in cuerpo


def test_miembros_ordenados_por_antiguedad_con_nombre_y_rol(client, crear_piso_con_miembros):
    _, admin, miembros = crear_piso_con_miembros(2)
    lista = client.get("/api/pisos/mio", headers=miembros[1]["headers"]).json()["miembros"]
    assert [m["usuario_id"] for m in lista] == [admin["id"], miembros[0]["id"], miembros[1]["id"]]
    assert [m["rol"] for m in lista] == ["admin", "miembro", "miembro"]
    assert lista[0]["nombre"] == admin["nombre"]
    assert all(m["unido_en"] for m in lista)


def test_ver_piso_sin_piso_404(client, crear_usuario):
    u = crear_usuario()
    assert_error(client.get("/api/pisos/mio", headers=u["headers"]), 404, "sin_piso")

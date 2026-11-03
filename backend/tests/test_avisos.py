"""US4 · Publicar (HU-09), ver tablón (HU-10) y borrar avisos (HU-11)."""

from datetime import datetime

import pytest

from tests.conftest import assert_error


def publicar(client, usuario, texto="Mañana viene el fontanero"):
    return client.post("/api/avisos", json={"texto": texto}, headers=usuario["headers"])


# --- Publicar -------------------------------------------------------------

def test_publicar_aviso_guarda_autor_y_fecha(client, crear_piso_con_miembros):
    _, _, [luis] = crear_piso_con_miembros(1)
    r = publicar(client, luis)
    assert r.status_code == 201
    aviso = r.json()
    assert aviso["texto"] == "Mañana viene el fontanero"
    assert aviso["autor"] == {"id": luis["id"], "nombre": luis["nombre"]}
    assert datetime.fromisoformat(aviso["creado_en"]).tzinfo is not None


def test_publicar_recorta_espacios(client, crear_piso_con_miembros):
    _, admin, _ = crear_piso_con_miembros()
    assert publicar(client, admin, "  hola  ").json()["texto"] == "hola"


@pytest.mark.parametrize("texto", ["", "    ", "x" * 281])
def test_publicar_texto_invalido_400(client, crear_piso_con_miembros, texto):
    _, admin, _ = crear_piso_con_miembros()
    assert_error(publicar(client, admin, texto), 400, "datos_invalidos")


def test_publicar_280_caracteres_es_valido(client, crear_piso_con_miembros):
    _, admin, _ = crear_piso_con_miembros()
    assert publicar(client, admin, "x" * 280).status_code == 201


def test_publicar_sin_piso_404(client, crear_usuario):
    assert_error(publicar(client, crear_usuario()), 404, "sin_piso")


def test_publicar_sin_token_401(client):
    assert_error(client.post("/api/avisos", json={"texto": "hola"}), 401, "no_autenticado")


# --- Ver tablón -----------------------------------------------------------

def test_tablon_del_mas_reciente_al_mas_antiguo(client, crear_piso_con_miembros):
    _, admin, [luis] = crear_piso_con_miembros(1)
    for i, autor in enumerate([admin, luis, admin]):
        publicar(client, autor, f"aviso {i}")
    r = client.get("/api/avisos", headers=luis["headers"])
    assert r.status_code == 200
    assert [a["texto"] for a in r.json()] == ["aviso 2", "aviso 1", "aviso 0"]
    assert r.json()[1]["autor"]["id"] == luis["id"]


def test_tablon_vacio(client, crear_piso_con_miembros):
    _, admin, _ = crear_piso_con_miembros()
    assert client.get("/api/avisos", headers=admin["headers"]).json() == []


def test_tablon_nunca_muestra_avisos_de_otro_piso(client, crear_piso_con_miembros):
    _, admin_a, _ = crear_piso_con_miembros()
    _, admin_b, _ = crear_piso_con_miembros()
    publicar(client, admin_a, "piso A")
    publicar(client, admin_b, "piso B")
    assert [a["texto"] for a in client.get("/api/avisos", headers=admin_a["headers"]).json()] == ["piso A"]
    assert [a["texto"] for a in client.get("/api/avisos", headers=admin_b["headers"]).json()] == ["piso B"]


def test_tablon_sin_piso_404(client, crear_usuario):
    assert_error(client.get("/api/avisos", headers=crear_usuario()["headers"]), 404, "sin_piso")


# --- Borrar ---------------------------------------------------------------

def test_autor_borra_su_aviso(client, crear_piso_con_miembros):
    _, admin, [luis] = crear_piso_con_miembros(1)
    aviso = publicar(client, luis).json()
    assert client.delete(f"/api/avisos/{aviso['id']}", headers=luis["headers"]).status_code == 204
    assert client.get("/api/avisos", headers=admin["headers"]).json() == []


def test_admin_borra_aviso_ajeno(client, crear_piso_con_miembros):
    _, admin, [luis] = crear_piso_con_miembros(1)
    aviso = publicar(client, luis).json()
    assert client.delete(f"/api/avisos/{aviso['id']}", headers=admin["headers"]).status_code == 204


def test_otro_miembro_no_puede_borrar_403(client, crear_piso_con_miembros):
    _, admin, [luis, marta] = crear_piso_con_miembros(2)
    de_luis = publicar(client, luis).json()
    de_admin = publicar(client, admin).json()
    assert_error(client.delete(f"/api/avisos/{de_luis['id']}", headers=marta["headers"]), 403, "permiso_denegado")
    assert_error(client.delete(f"/api/avisos/{de_admin['id']}", headers=luis["headers"]), 403, "permiso_denegado")
    assert len(client.get("/api/avisos", headers=admin["headers"]).json()) == 2


def test_borrar_aviso_inexistente_404(client, crear_piso_con_miembros):
    _, admin, _ = crear_piso_con_miembros()
    assert_error(client.delete("/api/avisos/9999", headers=admin["headers"]), 404, "aviso_no_encontrado")


def test_borrar_aviso_de_otro_piso_404(client, crear_piso_con_miembros):
    _, admin_a, _ = crear_piso_con_miembros()
    _, admin_b, _ = crear_piso_con_miembros()
    aviso = publicar(client, admin_b).json()
    assert_error(client.delete(f"/api/avisos/{aviso['id']}", headers=admin_a["headers"]), 404, "aviso_no_encontrado")
    assert len(client.get("/api/avisos", headers=admin_b["headers"]).json()) == 1


def test_avisos_no_se_pueden_editar(client, crear_piso_con_miembros):
    _, admin, _ = crear_piso_con_miembros()
    aviso = publicar(client, admin).json()
    r = client.put(f"/api/avisos/{aviso['id']}", json={"texto": "cambiado"}, headers=admin["headers"])
    assert_error(r, 405, "metodo_no_permitido")

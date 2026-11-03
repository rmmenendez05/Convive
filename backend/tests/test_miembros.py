"""US5 · Expulsar (HU-06), abandonar (HU-07) y regenerar código (HU-08)."""

from sqlalchemy import func, select

from app.models import ROL_ADMIN, Miembro, Piso
from tests.conftest import assert_error


def publicar(client, usuario, texto="Hola"):
    r = client.post("/api/avisos", json={"texto": texto}, headers=usuario["headers"])
    assert r.status_code == 201
    return r.json()


def textos(client, usuario):
    return [a["texto"] for a in client.get("/api/avisos", headers=usuario["headers"]).json()]


def admins_del_piso(db_session_factory, piso_id):
    with db_session_factory() as db:
        return db.scalar(select(func.count()).where(Miembro.piso_id == piso_id, Miembro.rol == ROL_ADMIN))


# --- Expulsar -------------------------------------------------------------

def test_admin_expulsa_a_un_miembro(client, crear_piso_con_miembros):
    _, admin, [luis, marta] = crear_piso_con_miembros(2)
    publicar(client, luis, "de Luis")
    publicar(client, marta, "de Marta")

    r = client.delete(f"/api/pisos/mio/miembros/{luis['id']}", headers=admin["headers"])
    assert r.status_code == 204
    assert_error(client.get("/api/pisos/mio", headers=luis["headers"]), 404, "sin_piso")
    ids = [m["usuario_id"] for m in client.get("/api/pisos/mio", headers=admin["headers"]).json()["miembros"]]
    assert luis["id"] not in ids
    assert textos(client, admin) == ["de Marta"]


def test_miembro_no_puede_expulsar_403(client, crear_piso_con_miembros):
    _, admin, [luis, marta] = crear_piso_con_miembros(2)
    r = client.delete(f"/api/pisos/mio/miembros/{marta['id']}", headers=luis["headers"])
    assert_error(r, 403, "permiso_denegado")
    r = client.delete(f"/api/pisos/mio/miembros/{admin['id']}", headers=luis["headers"])
    assert_error(r, 403, "permiso_denegado")


def test_admin_no_puede_expulsarse_400(client, crear_piso_con_miembros):
    _, admin, _ = crear_piso_con_miembros(1)
    r = client.delete(f"/api/pisos/mio/miembros/{admin['id']}", headers=admin["headers"])
    assert_error(r, 400, "no_puede_expulsarse")


def test_expulsar_a_quien_no_es_miembro_404(client, crear_piso_con_miembros, crear_usuario):
    _, admin, _ = crear_piso_con_miembros()
    _, _, [de_otro_piso] = crear_piso_con_miembros(1)
    sin_piso = crear_usuario()
    for objetivo in (de_otro_piso["id"], sin_piso["id"], 9999):
        r = client.delete(f"/api/pisos/mio/miembros/{objetivo}", headers=admin["headers"])
        assert_error(r, 404, "miembro_no_encontrado")


def test_expulsar_sin_piso_404(client, crear_usuario):
    u = crear_usuario()
    assert_error(client.delete("/api/pisos/mio/miembros/1", headers=u["headers"]), 404, "sin_piso")


def test_expulsado_puede_unirse_a_otro_piso(client, crear_piso_con_miembros):
    _, admin, [luis] = crear_piso_con_miembros(1)
    otro, _, _ = crear_piso_con_miembros()
    client.delete(f"/api/pisos/mio/miembros/{luis['id']}", headers=admin["headers"])
    r = client.post("/api/pisos/unirse", json={"codigo": otro["codigo_invitacion"]}, headers=luis["headers"])
    assert r.status_code == 200


def test_expulsado_con_sesion_abierta_pierde_acceso(client, crear_piso_con_miembros):
    _, admin, [luis] = crear_piso_con_miembros(1)
    client.delete(f"/api/pisos/mio/miembros/{luis['id']}", headers=admin["headers"])
    assert_error(client.get("/api/avisos", headers=luis["headers"]), 404, "sin_piso")
    assert_error(client.post("/api/avisos", json={"texto": "x"}, headers=luis["headers"]), 404, "sin_piso")


# --- Abandonar ------------------------------------------------------------

def test_miembro_abandona_y_se_borran_solo_sus_avisos(client, crear_piso_con_miembros):
    _, admin, [luis] = crear_piso_con_miembros(1)
    publicar(client, admin, "de Ana")
    publicar(client, luis, "de Luis 1")
    publicar(client, luis, "de Luis 2")

    assert client.post("/api/pisos/mio/abandonar", headers=luis["headers"]).status_code == 204
    assert_error(client.get("/api/pisos/mio", headers=luis["headers"]), 404, "sin_piso")
    assert textos(client, admin) == ["de Ana"]


def test_admin_abandona_y_el_mas_antiguo_pasa_a_admin(client, crear_piso_con_miembros, db_session_factory):
    piso, admin, [luis, marta] = crear_piso_con_miembros(2)
    assert client.post("/api/pisos/mio/abandonar", headers=admin["headers"]).status_code == 204

    vista = client.get("/api/pisos/mio", headers=luis["headers"]).json()
    roles = {m["usuario_id"]: m["rol"] for m in vista["miembros"]}
    assert roles == {luis["id"]: "admin", marta["id"]: "miembro"}
    assert "codigo_invitacion" in vista
    assert admins_del_piso(db_session_factory, piso["id"]) == 1


def test_traspaso_desempata_por_id_si_se_unieron_a_la_vez(client, crear_piso_con_miembros, db_session_factory):
    piso, admin, [luis, marta] = crear_piso_con_miembros(2)
    with db_session_factory() as db:
        a, b = db.get(Miembro, luis["id"]), db.get(Miembro, marta["id"])
        b.unido_en = a.unido_en
        db.commit()
    client.post("/api/pisos/mio/abandonar", headers=admin["headers"])
    assert client.get("/api/auth/yo", headers=luis["headers"]).json()["rol"] == "admin"


def test_admin_unico_abandona_y_el_piso_se_elimina(client, crear_piso_con_miembros, db_session_factory):
    piso, admin, _ = crear_piso_con_miembros()
    publicar(client, admin)
    assert client.post("/api/pisos/mio/abandonar", headers=admin["headers"]).status_code == 204
    with db_session_factory() as db:
        assert db.get(Piso, piso["id"]) is None
    assert_error(client.get("/api/pisos/mio", headers=admin["headers"]), 404, "sin_piso")


def test_tras_eliminar_el_piso_su_codigo_no_sirve(client, crear_piso_con_miembros, crear_usuario):
    piso, admin, _ = crear_piso_con_miembros()
    client.post("/api/pisos/mio/abandonar", headers=admin["headers"])
    u = crear_usuario()
    r = client.post("/api/pisos/unirse", json={"codigo": piso["codigo_invitacion"]}, headers=u["headers"])
    assert_error(r, 404, "codigo_invalido")


def test_abandonar_sin_piso_404(client, crear_usuario):
    u = crear_usuario()
    assert_error(client.post("/api/pisos/mio/abandonar", headers=u["headers"]), 404, "sin_piso")


def test_quien_abandona_puede_crear_otro_piso(client, crear_piso_con_miembros):
    _, _, [luis] = crear_piso_con_miembros(1)
    client.post("/api/pisos/mio/abandonar", headers=luis["headers"])
    assert client.post("/api/pisos", json={"nombre": "Nuevo"}, headers=luis["headers"]).status_code == 201


# --- Regenerar código -----------------------------------------------------

def test_admin_regenera_codigo_y_el_anterior_deja_de_valer(client, crear_piso_con_miembros, crear_usuario):
    piso, admin, _ = crear_piso_con_miembros()
    r = client.post("/api/pisos/mio/codigo", headers=admin["headers"])
    assert r.status_code == 200
    nuevo = r.json()["codigo_invitacion"]
    assert nuevo != piso["codigo_invitacion"]

    u = crear_usuario()
    r = client.post("/api/pisos/unirse", json={"codigo": piso["codigo_invitacion"]}, headers=u["headers"])
    assert_error(r, 404, "codigo_invalido")
    assert client.post("/api/pisos/unirse", json={"codigo": nuevo}, headers=u["headers"]).status_code == 200
    assert client.get("/api/pisos/mio", headers=admin["headers"]).json()["codigo_invitacion"] == nuevo


def test_miembro_no_puede_regenerar_codigo_403(client, crear_piso_con_miembros):
    _, _, [luis] = crear_piso_con_miembros(1)
    assert_error(client.post("/api/pisos/mio/codigo", headers=luis["headers"]), 403, "permiso_denegado")


def test_regenerar_codigo_sin_piso_404(client, crear_usuario):
    u = crear_usuario()
    assert_error(client.post("/api/pisos/mio/codigo", headers=u["headers"]), 404, "sin_piso")


def test_siempre_hay_un_unico_admin(client, crear_piso_con_miembros, db_session_factory):
    piso, admin, [luis, marta, pepe] = crear_piso_con_miembros(3)
    client.delete(f"/api/pisos/mio/miembros/{marta['id']}", headers=admin["headers"])
    assert admins_del_piso(db_session_factory, piso["id"]) == 1
    client.post("/api/pisos/mio/abandonar", headers=admin["headers"])
    assert admins_del_piso(db_session_factory, piso["id"]) == 1
    client.post("/api/pisos/mio/abandonar", headers=luis["headers"])
    assert admins_del_piso(db_session_factory, piso["id"]) == 1
    assert client.get("/api/auth/yo", headers=pepe["headers"]).json()["rol"] == "admin"

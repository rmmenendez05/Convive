"""SC-004 · Ningún endpoint devuelve ni modifica datos de otro piso."""

import json


def test_ningun_endpoint_expone_ni_modifica_otro_piso(client, crear_piso_con_miembros):
    piso_a, admin_a, [miembro_a] = crear_piso_con_miembros(1, nombre="Piso A")
    piso_b, admin_b, [miembro_b] = crear_piso_con_miembros(1, nombre="Piso B")
    aviso_b = client.post("/api/avisos", json={"texto": "secreto de B"}, headers=miembro_b["headers"]).json()

    respuestas = [
        client.get("/api/pisos/mio", headers=admin_a["headers"]),
        client.get("/api/avisos", headers=admin_a["headers"]),
        client.get("/api/auth/yo", headers=admin_a["headers"]),
        client.delete(f"/api/avisos/{aviso_b['id']}", headers=admin_a["headers"]),
        client.delete(f"/api/pisos/mio/miembros/{miembro_b['id']}", headers=admin_a["headers"]),
        client.post("/api/pisos/mio/codigo", headers=admin_a["headers"]),
    ]
    volcado = json.dumps([r.json() for r in respuestas if r.content])
    for dato_de_b in ("Piso B", "secreto de B", piso_b["codigo_invitacion"], miembro_b["nombre"], admin_b["nombre"]):
        assert dato_de_b not in volcado

    # El piso B sigue intacto.
    vista_b = client.get("/api/pisos/mio", headers=admin_b["headers"]).json()
    assert vista_b["codigo_invitacion"] == piso_b["codigo_invitacion"]
    assert {m["usuario_id"] for m in vista_b["miembros"]} == {admin_b["id"], miembro_b["id"]}
    assert [a["texto"] for a in client.get("/api/avisos", headers=admin_b["headers"]).json()] == ["secreto de B"]
    assert piso_a["id"] != piso_b["id"]
    assert miembro_a["id"] != miembro_b["id"]

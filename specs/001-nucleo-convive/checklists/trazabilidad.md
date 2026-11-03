# Trazabilidad: criterios de aceptación → tests

**Feature**: [spec.md](../spec.md) · Generado en T058 · 2026-11-03

Backend: `backend/tests/` (pytest, 95 tests). Frontend: `frontend/src/__tests__/` (Vitest, 36 tests).

## US1 · Crear cuenta e iniciar sesión

| Criterio | Tests |
| --- | --- |
| 1. Registro correcto | `test_auth.py::test_registro_correcto`, `test_registro_nombre_de_40_es_valido`, `test_registro_password_de_8_es_valida` · `acceso.test.jsx` "registro correcto…" |
| 2. Email duplicado → `email_ya_registrado` | `test_auth.py::test_registro_email_duplicado_409`, `…_con_mayusculas_409`, `test_registro_simultaneo_mismo_email_devuelve_409` · `acceso.test.jsx` "muestra email_ya_registrado…" |
| 3. Contraseña corta, email o nombre no válidos → 400 | `test_auth.py::test_registro_password_corta_400`, `test_registro_email_mal_formado_400`, `test_registro_nombre_invalido_400`, `test_registro_sin_nombre_400` |
| 4. Login correcto → sesión | `test_auth.py::test_login_correcto_devuelve_token`, `test_login_no_distingue_mayusculas_en_email` · `acceso.test.jsx` "login correcto con piso…" |
| 5. Error genérico idéntico | `test_auth.py::test_login_password_incorrecta_y_email_inexistente_dan_el_mismo_error` · `acceso.test.jsx` "login fallido…" |

## US2 · Crear un piso o unirse

| Criterio | Tests |
| --- | --- |
| 1. Crear piso, código de 8, creador admin | `test_pisos.py::test_crear_piso_correcto`, `test_crear_piso_sin_direccion` · `bienvenida.test.jsx` "crear piso…" |
| 2. Nombre no válido → 400 | `test_pisos.py::test_crear_piso_nombre_invalido_400`, `test_crear_piso_direccion_larga_400` |
| 3. Ya tiene piso → `ya_tiene_piso` | `test_pisos.py::test_crear_piso_teniendo_piso_409`, `test_unirse_teniendo_piso_409` |
| 4. Unirse con código válido | `test_pisos.py::test_unirse_con_codigo_valido`, `test_unirse_con_codigo_en_minusculas_y_espacios` · `bienvenida.test.jsx` "unirse con código…" |
| 5. Código inexistente → 404 | `test_pisos.py::test_unirse_codigo_inexistente_404` · `bienvenida.test.jsx` "muestra codigo_invalido" |

## US3 · Ver mi piso

| Criterio | Tests |
| --- | --- |
| 1. Nombre, dirección, miembros y rol | `test_pisos.py::test_miembros_ordenados_por_antiguedad_con_nombre_y_rol` · `piso.test.jsx` "lista los miembros…" |
| 2. Admin ve el código | `test_pisos.py::test_admin_ve_el_codigo` · `piso.test.jsx` "el admin ve el código…" |
| 3. Miembro no ve el código | `test_pisos.py::test_miembro_no_ve_el_codigo` · `piso.test.jsx` "un miembro no ve el código" |
| 4. Sin piso → `sin_piso` | `test_pisos.py::test_ver_piso_sin_piso_404` · `bienvenida.test.jsx` "sin piso, /piso redirige…" |

## US4 · Tablón de avisos

| Criterio | Tests |
| --- | --- |
| 1. Publicar con autor y fecha | `test_avisos.py::test_publicar_aviso_guarda_autor_y_fecha`, `test_publicar_280_caracteres_es_valido` · `tablon.test.jsx` "publicar añade…" |
| 2. Vacío o > 280 → 400 | `test_avisos.py::test_publicar_texto_invalido_400` · `tablon.test.jsx` "muestra el error al publicar", "cuenta los caracteres…" |
| 3. Orden descendente | `test_avisos.py::test_tablon_del_mas_reciente_al_mas_antiguo` |
| 4. Nunca avisos de otro piso | `test_avisos.py::test_tablon_nunca_muestra_avisos_de_otro_piso`, `test_aislamiento.py` |
| 5. Borra autor o admin | `test_avisos.py::test_autor_borra_su_aviso`, `test_admin_borra_aviso_ajeno` · `tablon.test.jsx` "el admin puede borrar…" |
| 6. Otro miembro → 403 | `test_avisos.py::test_otro_miembro_no_puede_borrar_403` · `tablon.test.jsx` "un miembro solo puede borrar…" |
| 7. Inexistente u otro piso → 404 | `test_avisos.py::test_borrar_aviso_inexistente_404`, `test_borrar_aviso_de_otro_piso_404` |

## US5 · Gestionar los miembros

| Criterio | Tests |
| --- | --- |
| 1. Expulsar; queda sin piso y sin avisos | `test_miembros.py::test_admin_expulsa_a_un_miembro` · `miembros.test.jsx` "el admin expulsa…" |
| 2. No admin → 403 | `test_miembros.py::test_miembro_no_puede_expulsar_403` · `miembros.test.jsx` "un miembro no ve…" |
| 3. Expulsarse → 400 | `test_miembros.py::test_admin_no_puede_expulsarse_400` |
| 4. No miembro → 404 | `test_miembros.py::test_expulsar_a_quien_no_es_miembro_404` |
| 5. Abandonar; se borran sus avisos | `test_miembros.py::test_miembro_abandona_y_se_borran_solo_sus_avisos` · `miembros.test.jsx` "abandonar tras confirmar…" |
| 6. Admin abandona → el más antiguo es admin | `test_miembros.py::test_admin_abandona_y_el_mas_antiguo_pasa_a_admin`, `test_traspaso_desempata_por_id…`, `test_siempre_hay_un_unico_admin` · `miembros.test.jsx` "el miembro que hereda…" |
| 7. Único miembro abandona → piso eliminado | `test_miembros.py::test_admin_unico_abandona_y_el_piso_se_elimina`, `test_tras_eliminar_el_piso_su_codigo_no_sirve` |
| 8. Regenerar código; el anterior deja de valer | `test_miembros.py::test_admin_regenera_codigo_y_el_anterior_deja_de_valer` · `miembros.test.jsx` "el admin regenera…" |
| 9. No admin regenera → 403 | `test_miembros.py::test_miembro_no_puede_regenerar_codigo_403` |

## Casos límite y transversales

| Requisito | Tests |
| --- | --- |
| Expulsado o quien abandona puede unirse / crear otro piso | `test_miembros.py::test_expulsado_puede_unirse_a_otro_piso`, `test_quien_abandona_puede_crear_otro_piso` |
| Expulsado con sesión abierta pierde acceso | `test_miembros.py::test_expulsado_con_sesion_abierta_pierde_acceso` |
| Sin sesión → 401 (FR-006) | `test_errores.py::test_sin_token_devuelve_401`, `test_token_manipulado…`, `test_token_caducado…`, `test_token_dura_24_horas` · `acceso.test.jsx` "con un token caducado…" |
| Aislamiento entre pisos (FR-019, SC-004) | `test_aislamiento.py` |
| Formato único de error (FR-020) | `test_errores.py` (400, 404, 405, 500) · `conftest.assert_error` en todos los tests de error |
| Persistencia (FR-021, SC-005) | `test_migraciones.py` + validación manual con `docker compose down`/`up` (T059) |
| Redirecciones (FR-022) | `acceso.test.jsx`, `bienvenida.test.jsx` |
| Bilingüe (FR-023, FR-024) | `test_errores.py::test_mensaje_en_ingles…`, `…_espanol_por_defecto` · `i18n.test.jsx`, `client.test.js` |
| Avisos no editables (FR-018) | `test_avisos.py::test_avisos_no_se_pueden_editar` |

# API Contract: Núcleo de Convive

- Base: `/api`. JSON UTF-8. Fechas ISO 8601 en UTC.
- Autenticación: `Authorization: Bearer <token>` en todo salvo `/auth/registro` y `/auth/login`.
- Idioma de `message`: cabecera `Accept-Language` (`es` por defecto, `en`).
- Error: `{"error": {"code": "<code>", "message": "<texto>", "details"?: [...]}}`.

## Errores comunes a todos los endpoints autenticados

| HTTP | code | Cuándo |
| --- | --- | --- |
| 401 | `no_autenticado` | Falta el token, es inválido, ha caducado o el usuario ya no existe |
| 400 | `datos_invalidos` | Cuerpo que no cumple el esquema (incluye `details`) |
| 404 | `sin_piso` | La acción requiere piso y el usuario no tiene |

## Auth

### POST /auth/registro — HU-01

Body `{ "email", "password", "nombre" }` → **201** `{ "id", "email", "nombre" }`

| HTTP | code | Cuándo |
| --- | --- | --- |
| 400 | `datos_invalidos` | Email mal formado, contraseña < 8, nombre vacío o > 40 |
| 409 | `email_ya_registrado` | El email (sin distinguir mayúsculas) ya existe |

### POST /auth/login — HU-02

Body `{ "email", "password" }` → **200** `{ "token", "expira_en", "usuario": { "id", "email", "nombre" } }`

| HTTP | code | Cuándo |
| --- | --- | --- |
| 401 | `credenciales_invalidas` | Email inexistente o contraseña incorrecta (mismo mensaje) |

### GET /auth/yo

→ **200** `{ "id", "email", "nombre", "piso_id": int | null, "rol": "admin" | "miembro" | null }`
(lo usa el frontend para decidir entre `/bienvenida` y `/piso`).

## Pisos

Representación `Piso`:

```json
{
  "id": 1, "nombre": "Calle Mayor 3", "direccion": null,
  "codigo_invitacion": "K7Q2M9XA",
  "miembros": [
    { "usuario_id": 1, "nombre": "Ana", "rol": "admin", "unido_en": "2026-11-03T10:00:00Z" }
  ]
}
```

`codigo_invitacion` solo aparece si quien consulta es el administrador (la clave se omite).
`miembros` va ordenado por `unido_en` ascendente.

### POST /pisos — HU-03

Body `{ "nombre", "direccion"? }` → **201** `Piso` (con código; el creador es admin)

| HTTP | code | Cuándo |
| --- | --- | --- |
| 400 | `datos_invalidos` | Nombre vacío o > 60, dirección > 200 |
| 409 | `ya_tiene_piso` | El usuario ya es miembro de un piso |

### POST /pisos/unirse — HU-04

Body `{ "codigo" }` → **200** `Piso` (vista de miembro, sin código)

| HTTP | code | Cuándo |
| --- | --- | --- |
| 404 | `codigo_invalido` | No existe ningún piso con ese código |
| 409 | `ya_tiene_piso` | El usuario ya es miembro de un piso |

### GET /pisos/mio — HU-05

→ **200** `Piso` · errores comunes (`404 sin_piso`).

### DELETE /pisos/mio/miembros/{usuario_id} — HU-06

→ **204** (se borran los avisos del expulsado en el piso)

| HTTP | code | Cuándo |
| --- | --- | --- |
| 403 | `permiso_denegado` | Quien llama no es admin |
| 400 | `no_puede_expulsarse` | El admin intenta expulsarse a sí mismo |
| 404 | `miembro_no_encontrado` | El usuario no es miembro de este piso |

### POST /pisos/mio/abandonar — HU-07

→ **204**. Efectos: borra sus avisos del piso; si era admin, traspasa el rol al más antiguo; si
era el único, elimina el piso. Errores comunes (`404 sin_piso`).

### POST /pisos/mio/codigo — HU-08

→ **200** `{ "codigo_invitacion": "NUEVO123" }`

| HTTP | code | Cuándo |
| --- | --- | --- |
| 403 | `permiso_denegado` | Quien llama no es admin |

## Avisos

Representación `Aviso`: `{ "id", "texto", "autor": { "id", "nombre" }, "creado_en" }`

### POST /avisos — HU-09

Body `{ "texto" }` → **201** `Aviso`

| HTTP | code | Cuándo |
| --- | --- | --- |
| 400 | `datos_invalidos` | Texto vacío (tras recortar) o > 280 |

### GET /avisos — HU-10

→ **200** `[Aviso]` del piso del usuario, de más reciente a más antiguo.

### DELETE /avisos/{id} — HU-11

→ **204**

| HTTP | code | Cuándo |
| --- | --- | --- |
| 403 | `permiso_denegado` | No es el autor ni el admin |
| 404 | `aviso_no_encontrado` | No existe o pertenece a otro piso |

## Catálogo de mensajes (es / en)

| code | es | en |
| --- | --- | --- |
| `datos_invalidos` | Los datos enviados no son válidos | The submitted data is not valid |
| `no_autenticado` | Tienes que iniciar sesión | You need to sign in |
| `credenciales_invalidas` | Email o contraseña incorrectos | Incorrect email or password |
| `email_ya_registrado` | Ya existe una cuenta con ese email | An account with that email already exists |
| `ya_tiene_piso` | Ya perteneces a un piso | You already belong to a flat |
| `sin_piso` | Todavía no perteneces a ningún piso | You don't belong to a flat yet |
| `codigo_invalido` | No hay ningún piso con ese código | There is no flat with that code |
| `permiso_denegado` | No tienes permiso para hacer esto | You are not allowed to do this |
| `no_puede_expulsarse` | No puedes expulsarte a ti mismo | You cannot remove yourself |
| `miembro_no_encontrado` | Esa persona no es miembro del piso | That person is not a member of the flat |
| `aviso_no_encontrado` | El aviso no existe | The notice does not exist |
| `error_interno` | Ha ocurrido un error inesperado | An unexpected error occurred |

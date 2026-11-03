# Data Model: Núcleo de Convive

Basado en SPECS.md §5.1 y en las aclaraciones de la spec. Fechas en UTC.

## usuarios

| Campo | Tipo | Reglas |
| --- | --- | --- |
| id | INTEGER PK | autoincremental |
| email | VARCHAR(254) | `UNIQUE`, guardado en minúsculas y sin espacios |
| password_hash | VARCHAR(255) | hash Argon2id; nunca se devuelve |
| nombre | VARCHAR(40) | obligatorio, 1–40 caracteres tras recortar espacios |
| creado_en | DATETIME | por defecto ahora |

## pisos

| Campo | Tipo | Reglas |
| --- | --- | --- |
| id | INTEGER PK | |
| nombre | VARCHAR(60) | obligatorio, 1–60 caracteres tras recortar |
| direccion | VARCHAR(200) NULL | opcional; cadena vacía se guarda como NULL |
| codigo_invitacion | CHAR(8) | `UNIQUE`, `[A-Z0-9]{8}` |
| creado_en | DATETIME | |

## miembros

| Campo | Tipo | Reglas |
| --- | --- | --- |
| usuario_id | INTEGER PK, FK → usuarios.id | PK ⇒ un piso por usuario |
| piso_id | INTEGER FK → pisos.id `ON DELETE CASCADE` | índice |
| rol | VARCHAR(10) | `CHECK (rol IN ('admin','miembro'))` |
| unido_en | DATETIME | ordena la antigüedad |

Invariante (servicio + test): cada piso con miembros tiene exactamente un `admin`.

## avisos

| Campo | Tipo | Reglas |
| --- | --- | --- |
| id | INTEGER PK | |
| piso_id | INTEGER FK → pisos.id `ON DELETE CASCADE` | índice `(piso_id, creado_en DESC)` |
| autor_id | INTEGER FK → usuarios.id | |
| texto | VARCHAR(280) | 1–280 caracteres tras recortar |
| creado_en | DATETIME | orden del tablón (desc), desempate por `id` desc |

## Transiciones de estado

```text
Usuario sin piso ──crear piso──▶ admin de su piso
Usuario sin piso ──unirse(código)──▶ miembro
miembro ──abandonar / ser expulsado──▶ sin piso   (se borran sus avisos de ese piso)
admin ──abandonar, quedan otros──▶ sin piso; el miembro más antiguo pasa a admin
admin ──abandonar, era el único──▶ sin piso; el piso y sus avisos se eliminan
admin ──regenerar código──▶ nuevo código; el anterior deja de existir
```

## Validaciones (Pydantic)

- `RegistroIn`: `email: EmailStr`, `password: str (min 8, max 128)`, `nombre: str (1–40)`.
- `LoginIn`: `email: str`, `password: str`.
- `PisoIn`: `nombre: str (1–60)`, `direccion: str | None (max 200)`.
- `UnirseIn`: `codigo: str` (se normaliza; si no tiene 8 caracteres alfanuméricos → 404
  `codigo_invalido`, igual que uno inexistente).
- `AvisoIn`: `texto: str (1–280)`.

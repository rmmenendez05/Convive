# Research: Núcleo de Convive

Decisiones técnicas tomadas en la Phase 0 del plan. Ninguna queda como NEEDS CLARIFICATION.

## R1. Hash de contraseñas

- **Decision**: Argon2id con `argon2-cffi` (`PasswordHasher` con parámetros por defecto).
- **Rationale**: Recomendado por OWASP; la constitución permite bcrypt o argon2. API sencilla
  (`hash`, `verify`, `check_needs_rehash`).
- **Alternatives**: bcrypt (`bcrypt`/`passlib`): límite de 72 bytes y passlib sin mantenimiento.

## R2. Autenticación

- **Decision**: JWT HS256 con PyJWT. Claims `sub` (id de usuario), `iat`, `exp` = 24 h. Clave en
  la variable `JWT_SECRET`. Cabecera `Authorization: Bearer <token>`.
- **Rationale**: Sin estado en servidor, encaja con "sin cierre de sesión en servidor" y con la
  duración de 24 h aclarada. Al validar el token se comprueba además que el usuario existe.
- **Alternatives**: sesiones en BD (más tablas y limpieza), OAuth2 completo (excesivo).
- **Login sin enumeración**: si el email no existe se ejecuta igualmente una verificación contra
  un hash ficticio para igualar tiempos; mismo error `credenciales_invalidas` en ambos casos.

## R3. Formato único de errores

- **Decision**: excepción propia `AppError(status, code, params)` y manejadores globales para
  `AppError`, `RequestValidationError` (→ 400 `datos_invalidos`, con `details` por campo),
  `HTTPException` de Starlette (401/404/405 genéricos) y `Exception` (500 `error_interno`).
- **Rationale**: FastAPI responde 422 por defecto; la constitución exige 400 y un único formato.
- **Formato**: `{"error": {"code": "ya_tiene_piso", "message": "Ya perteneces a un piso"}}`.
  En validación se añade `"details": [{"field": "password", "code": "min_length"}]`.

## R4. Internacionalización (es/en)

- **Decision (backend)**: catálogo `app/core/i18n.py` con `{code: {"es": ..., "en": ...}}`. El
  idioma se elige con la cabecera `Accept-Language` (primer valor `es` o `en`; si no, `es`).
  Solo traduce `message`; `code` nunca cambia.
- **Decision (frontend)**: diccionarios `es.js`/`en.js` + `LangContext` + hook `useT()`. Idioma
  guardado en `localStorage` (`convive.lang`), por defecto `es`. El cliente API envía
  `Accept-Language` con el idioma activo. La UI muestra el `message` del servidor, y si falta usa
  su propia traducción del `code`.
- **Rationale**: Dos idiomas y unas decenas de cadenas no justifican una dependencia
  (constitución II, YAGNI).
- **Alternatives**: `i18next` + `react-i18next` (válido si crece el número de idiomas).

## R5. Base de datos y migraciones

- **Decision**: SQLAlchemy 2.x síncrono con `Session` por petición; `PRAGMA foreign_keys=ON` en
  cada conexión; Alembic con una migración inicial `0001_nucleo`. El contenedor del backend
  ejecuta `alembic upgrade head` antes de `uvicorn`.
- **Rationale**: SQLite no gana nada con async; síncrono es más simple de probar.
- **Tests**: SQLite en memoria con `StaticPool` y `Base.metadata.create_all` por test; un test
  aparte comprueba que `alembic upgrade head` crea el mismo esquema.

## R6. Código de invitación

- **Decision**: 8 caracteres de `A–Z0–9` con `secrets.choice`; índice `UNIQUE`; se reintenta ante
  colisión (máx. 5). Al unirse, el código recibido se pasa a mayúsculas y se recortan espacios.
- **Rationale**: 36⁸ ≈ 2,8·10¹² combinaciones; colisiones prácticamente imposibles.

## R7. Membresía y reglas de piso

- **Decision**: `miembros.usuario_id` es clave primaria (un piso por usuario, garantizado por la
  BD). El "miembro más antiguo" es el de menor `unido_en`, desempate por menor `usuario_id`.
  Abandonar/expulsar se hace en una transacción: borrar avisos del usuario en ese piso → borrar
  membresía → traspasar admin o eliminar el piso si queda vacío.
- **Aislamiento**: el piso nunca llega por parámetro; siempre se deriva del usuario autenticado.
  Un aviso o miembro de otro piso responde 404 (no 403) para no revelar su existencia.

## R8. Frontend

- **Decision**: React Router 7 en modo declarativo (`<BrowserRouter>` + `<Routes>`, que permite
  probar con `<MemoryRouter>`); `RutaProtegida` que
  redirige a `/login` sin token y a `/bienvenida` sin piso; formularios con `useActionState`
  (SPECS.md §5.3). Token en memoria (estado de `AuthContext`) y en `localStorage`
  (`convive.token`); ante un 401 se borra y se navega a `/login`.
- **Tests**: Vitest + jsdom + RTL; el módulo `api/client.js` se simula con `vi.mock`.

## R9. Docker

- **Decision**: `backend` desde `python:3.12-slim`, usuario no root, puerto 8000, volumen
  `convive-data:/data`. `frontend` multi-etapa `node:22-alpine` → `nginx:alpine`, puerto 80
  publicado en el host como 5173; `nginx.conf` con `try_files $uri /index.html` y
  `location /api/ { proxy_pass http://backend:8000; }`.
- **Configuración**: `.env.example` con `JWT_SECRET`, `JWT_EXPIRES_HOURS=24`,
  `DATABASE_URL=sqlite:////data/convive.db`, `CORS_ORIGINS` (solo para desarrollo con Vite).

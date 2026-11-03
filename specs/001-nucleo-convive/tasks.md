---

description: "Lista de tareas del núcleo de Convive"
---

# Tasks: Núcleo de Convive (cuentas, pisos y tablón)

**Input**: Design documents from `/specs/001-nucleo-convive/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md

**Tests**: Obligatorios por la constitución (principio III). En cada historia los tests se
escriben primero y deben fallar antes de implementar.

**Organization**: Tareas agrupadas por historia de usuario; cada historia se puede probar sola.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Se puede hacer en paralelo (otro fichero, sin dependencias pendientes)
- **[Story]**: Historia a la que pertenece (US1…US5)
- Rutas según la estructura de [plan.md](./plan.md): `backend/app/`, `backend/tests/`,
  `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estructura del repositorio, dependencias y Docker

- [ ] T001 Crear la estructura de carpetas `backend/app/{core,models,schemas,routers,services}`, `backend/tests/`, `frontend/src/{api,context,i18n,components,pages,__tests__}` según plan.md
- [ ] T002 Crear `backend/requirements.txt` con versiones exactas (fastapi, uvicorn, sqlalchemy, alembic, pydantic, email-validator, pyjwt, argon2-cffi, pytest, httpx) y `backend/pytest.ini`
- [ ] T003 [P] Inicializar el frontend con Vite + React 19 en `frontend/package.json` (react-router, vitest, @testing-library/react, @testing-library/user-event, jsdom) y configurar Vitest en `frontend/vite.config.js` (entorno jsdom, proxy `/api` → `localhost:8000`)
- [ ] T004 [P] Crear `.env.example` en la raíz con `JWT_SECRET`, `JWT_EXPIRES_HOURS=24`, `DATABASE_URL=sqlite:////data/convive.db`, `CORS_ORIGINS`
- [ ] T005 [P] Crear `backend/Dockerfile` (python:3.12-slim, usuario no root, `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000`)
- [ ] T006 [P] Crear `frontend/Dockerfile` multi-etapa (node:22-alpine → nginx:alpine) y `frontend/nginx.conf` (fallback SPA + `location /api/` → `http://backend:8000`)
- [ ] T007 Crear `docker-compose.yml` con servicios `backend` (8000) y `frontend` (80 → 5173), volumen `convive-data:/data` y `env_file: .env`; comprobar que `docker compose up --build` levanta ambos
- [ ] T008 [P] Crear `README.md` con arranque con Docker y cómo ejecutar tests de backend y frontend (según quickstart.md)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Piezas que necesitan todas las historias

**⚠️ CRITICAL**: Ninguna historia empieza hasta terminar esta fase

- [ ] T009 Implementar `backend/app/core/config.py` (lectura de variables de entorno, sin valores secretos por defecto en producción)
- [ ] T010 Implementar `backend/app/core/db.py` (engine, `SessionLocal`, `Base`, `PRAGMA foreign_keys=ON`) y `get_db` en `backend/app/deps.py`
- [ ] T011 [P] Crear modelos SQLAlchemy en `backend/app/models/{usuario,piso,miembro,aviso}.py` según data-model.md
- [ ] T012 Configurar Alembic (`backend/alembic.ini`, `backend/alembic/env.py`) y crear la migración `backend/alembic/versions/0001_nucleo.py` con las cuatro tablas, índices y restricciones
- [ ] T013 [P] Implementar el catálogo bilingüe `backend/app/core/i18n.py` (códigos de contracts/api.md, elección por `Accept-Language`, `es` por defecto)
- [ ] T014 Implementar `backend/app/core/errors.py`: `AppError` y manejadores para `AppError`, `RequestValidationError` (→ 400 `datos_invalidos` con `details`), `HTTPException` y `Exception` (500 `error_interno`); registrarlos en `backend/app/main.py`
- [ ] T015 [P] Implementar `backend/app/core/security.py`: hash/verificación Argon2id, creación y validación de JWT de 24 h
- [ ] T016 Implementar `get_usuario_actual` (401 `no_autenticado`) y `get_miembro_actual` (404 `sin_piso`) en `backend/app/deps.py`
- [ ] T017 Crear `backend/tests/conftest.py` (SQLite en memoria con `StaticPool`, override de `get_db`, `client`, fábricas `crear_usuario`, `login`, `crear_piso_con_miembros`)
- [ ] T018 [P] Tests del formato de error y del idioma en `backend/tests/test_errores.py` (400 por validación con formato único, 401 sin token / token caducado / token manipulado, mensaje en `en` con `Accept-Language: en`, ruta inexistente 404 con formato único)
- [ ] T019 [P] Test de migraciones en `backend/tests/test_migraciones.py` (`alembic upgrade head` sobre una BD temporal crea las tablas esperadas)
- [ ] T020 [P] Implementar el cliente único `frontend/src/api/client.js` (base `/api`, cabeceras `Authorization` y `Accept-Language`, parseo del error `{error:{code,message}}` a una excepción `ApiError`, borrado del token ante 401)
- [ ] T021 [P] Implementar i18n del frontend: `frontend/src/i18n/{es,en}.js`, `frontend/src/context/LangContext.jsx`, hook `useT` y `frontend/src/components/SelectorIdioma.jsx` (persistencia en `localStorage` `convive.lang`)
- [ ] T022 Implementar `frontend/src/context/AuthContext.jsx` (token en memoria + `localStorage` `convive.token`, usuario actual vía `GET /auth/yo`), `frontend/src/components/RutaProtegida.jsx` y el router en `frontend/src/App.jsx`
- [ ] T023 [P] Tests del frontend base en `frontend/src/__tests__/client.test.js` (cabeceras, parseo de errores, 401) y `frontend/src/__tests__/i18n.test.jsx` (idioma por defecto, cambio y persistencia)

**Checkpoint**: Base lista; las historias pueden empezar

---

## Phase 3: User Story 1 - Crear cuenta e iniciar sesión (Priority: P1) 🎯 MVP

**Goal**: Un visitante se registra (email, contraseña, nombre) e inicia sesión.

**Independent Test**: Registrar, iniciar sesión y obtener token; credenciales erróneas → 401
genérico.

### Tests for User Story 1 ⚠️

- [ ] T024 [P] [US1] Tests de `POST /api/auth/registro` en `backend/tests/test_auth.py`: 201; 409 `email_ya_registrado` (también con distinto uso de mayúsculas); 400 por email mal formado, contraseña < 8, nombre vacío y nombre > 40; la contraseña no se guarda en claro
- [ ] T025 [P] [US1] Tests de `POST /api/auth/login` y `GET /api/auth/yo` en `backend/tests/test_auth.py`: 200 con token; 401 `credenciales_invalidas` idéntico para email inexistente y contraseña errónea; `/auth/yo` devuelve `piso_id: null` sin piso
- [ ] T026 [P] [US1] Tests de pantallas en `frontend/src/__tests__/acceso.test.jsx`: registro correcto redirige a login/bienvenida; error `email_ya_registrado` visible; login fallido muestra el mensaje; sin token, una ruta protegida redirige a `/login`

### Implementation for User Story 1

- [ ] T027 [P] [US1] Esquemas `RegistroIn`, `LoginIn`, `UsuarioOut`, `TokenOut`, `YoOut` en `backend/app/schemas/auth.py`
- [ ] T028 [US1] Servicio `backend/app/services/auth_service.py`: registrar (email en minúsculas, unicidad), autenticar sin enumeración (hash ficticio), datos de `/auth/yo`
- [ ] T029 [US1] Router `backend/app/routers/auth.py` (`/registro`, `/login`, `/yo`) registrado en `backend/app/main.py`
- [ ] T030 [P] [US1] Páginas `frontend/src/pages/Registro.jsx` y `frontend/src/pages/Login.jsx` con `useActionState`, errores traducidos y `frontend/src/components/FormError.jsx`

**Checkpoint**: US1 funcional y probada de forma independiente

---

## Phase 4: User Story 2 - Crear un piso o unirse a uno (Priority: P1)

**Goal**: Un usuario sin piso crea uno (admin) o se une con código.

**Independent Test**: A crea piso y recibe código; B se une con él; ambos quedan en el piso.

### Tests for User Story 2 ⚠️

- [ ] T031 [P] [US2] Tests de `POST /api/pisos` en `backend/tests/test_pisos.py`: 201 con código `[A-Z0-9]{8}` y creador admin; 400 nombre vacío / > 60 / dirección > 200; 409 `ya_tiene_piso`; 401 sin token
- [ ] T032 [P] [US2] Tests de `POST /api/pisos/unirse` en `backend/tests/test_pisos.py`: 200 como miembro; código en minúsculas válido; 404 `codigo_invalido`; 409 `ya_tiene_piso`; códigos de dos pisos distintos son diferentes
- [ ] T033 [P] [US2] Tests de `frontend/src/__tests__/bienvenida.test.jsx`: crear piso y unirse llevan a `/piso`; error `codigo_invalido` visible; con piso, `/bienvenida` redirige a `/piso`

### Implementation for User Story 2

- [ ] T034 [P] [US2] Esquemas `PisoIn`, `UnirseIn`, `PisoOut` (código opcional), `MiembroOut` en `backend/app/schemas/piso.py`
- [ ] T035 [US2] Servicio `backend/app/services/piso_service.py`: `generar_codigo` (único, reintentos), `crear_piso`, `unirse`
- [ ] T036 [US2] Router `backend/app/routers/pisos.py` con `POST /pisos` y `POST /pisos/unirse`, registrado en `backend/app/main.py`
- [ ] T037 [US2] Página `frontend/src/pages/Bienvenida.jsx` (formularios crear / unirse con `useActionState`)

**Checkpoint**: US1 + US2 funcionan (MVP mínimo: cuentas y pisos)

---

## Phase 5: User Story 3 - Ver mi piso (Priority: P2)

**Goal**: Un miembro ve nombre, dirección y miembros con rol; solo el admin ve el código.

**Independent Test**: Admin y miembro consultan el piso; solo el admin recibe el código.

### Tests for User Story 3 ⚠️

- [ ] T038 [P] [US3] Tests de `GET /api/pisos/mio` en `backend/tests/test_pisos.py`: admin ve código; miembro no recibe la clave `codigo_invitacion`; miembros ordenados por antigüedad; 404 `sin_piso`
- [ ] T039 [P] [US3] Tests de `frontend/src/__tests__/piso.test.jsx`: lista de miembros con rol; código visible solo para admin

### Implementation for User Story 3

- [ ] T040 [US3] `obtener_piso(usuario)` en `backend/app/services/piso_service.py` y `GET /pisos/mio` en `backend/app/routers/pisos.py`
- [ ] T041 [US3] Página `frontend/src/pages/Piso.jsx` (cabecera del piso, `frontend/src/components/ListaMiembros.jsx`, código para admin)

**Checkpoint**: US3 funcional

---

## Phase 6: User Story 4 - Tablón de avisos (Priority: P2)

**Goal**: Publicar, ver (más reciente primero) y borrar avisos con permisos.

**Independent Test**: A publica, B lo ve; A lo borra; C no puede borrar avisos ajenos.

### Tests for User Story 4 ⚠️

- [ ] T042 [P] [US4] Tests de `POST /api/avisos` y `GET /api/avisos` en `backend/tests/test_avisos.py`: 201 con autor y fecha; 400 vacío / solo espacios / > 280; orden descendente; nunca avisos de otro piso; 404 `sin_piso`
- [ ] T043 [P] [US4] Tests de `DELETE /api/avisos/{id}` en `backend/tests/test_avisos.py`: 204 por autor; 204 por admin; 403 `permiso_denegado` para otro miembro; 404 `aviso_no_encontrado` si no existe o es de otro piso
- [ ] T044 [P] [US4] Tests de `frontend/src/__tests__/tablon.test.jsx`: publicar añade el aviso arriba; contador de 280; botón borrar solo para autor o admin

### Implementation for User Story 4

- [ ] T045 [P] [US4] Esquemas `AvisoIn`, `AvisoOut` en `backend/app/schemas/aviso.py`
- [ ] T046 [US4] Servicio `backend/app/services/aviso_service.py` (publicar, listar del piso, borrar con permisos)
- [ ] T047 [US4] Router `backend/app/routers/avisos.py` registrado en `backend/app/main.py`
- [ ] T048 [US4] Componentes `frontend/src/components/Tablon.jsx` y `frontend/src/components/AvisoItem.jsx` integrados en `frontend/src/pages/Piso.jsx`

**Checkpoint**: US1–US4 funcionan

---

## Phase 7: User Story 5 - Gestionar los miembros del piso (Priority: P3)

**Goal**: Expulsar, abandonar (con traspaso de admin o borrado del piso) y regenerar código.

**Independent Test**: Piso de 3: regenerar código, expulsar a uno, el admin abandona y el
restante pasa a admin; al abandonar el último, el piso desaparece.

### Tests for User Story 5 ⚠️

- [ ] T049 [P] [US5] Tests de `DELETE /api/pisos/mio/miembros/{id}` en `backend/tests/test_miembros.py`: 204 y el expulsado queda sin piso y sin avisos; 403 no admin; 400 `no_puede_expulsarse`; 404 `miembro_no_encontrado` (incluido usuario de otro piso); el expulsado puede unirse a otro piso
- [ ] T050 [P] [US5] Tests de `POST /api/pisos/mio/abandonar` en `backend/tests/test_miembros.py`: miembro abandona y se borran sus avisos (los de otros siguen); admin abandona → admin el más antiguo (desempate por id); único miembro → piso y avisos eliminados; siempre un único admin; 404 `sin_piso`
- [ ] T051 [P] [US5] Tests de `POST /api/pisos/mio/codigo` en `backend/tests/test_miembros.py`: 200 código nuevo distinto; el anterior da 404 `codigo_invalido`; 403 no admin
- [ ] T052 [P] [US5] Tests de `frontend/src/__tests__/miembros.test.jsx`: botones de expulsar y regenerar solo para admin; confirmación integrada en la página antes de expulsar/abandonar; tras abandonar se va a `/bienvenida`

### Implementation for User Story 5

- [ ] T053 [US5] `expulsar`, `abandonar` (transacción: borrar avisos → borrar membresía → traspasar admin o eliminar piso) y `regenerar_codigo` en `backend/app/services/piso_service.py`
- [ ] T054 [US5] Endpoints `DELETE /pisos/mio/miembros/{usuario_id}`, `POST /pisos/mio/abandonar`, `POST /pisos/mio/codigo` en `backend/app/routers/pisos.py`
- [ ] T055 [US5] Acciones de gestión en `frontend/src/components/ListaMiembros.jsx` y `frontend/src/pages/Piso.jsx` (expulsar, abandonar, regenerar, con confirmación en página)

**Checkpoint**: Todas las historias del núcleo funcionan

---

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T056 [P] Test de aislamiento en `backend/tests/test_aislamiento.py`: con dos pisos, ningún endpoint devuelve ni modifica datos del otro (SC-004)
- [ ] T057 [P] Test de concurrencia de registro en `backend/tests/test_auth.py`: la restricción `UNIQUE` provoca 409 y no 500
- [ ] T058 Revisar que cada criterio de aceptación de spec.md tiene al menos un test (tabla de trazabilidad en `specs/001-nucleo-convive/checklists/trazabilidad.md`)
- [ ] T059 Validar quickstart.md de principio a fin con `docker compose up --build`, incluida la persistencia tras `down`/`up` (SC-005)
- [ ] T060 [P] Actualizar `docs/SPECS.md` y `docs/proceso-spec-kit.md` si el comportamiento final difiere de lo especificado

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias
- **Foundational (Phase 2)**: depende de Setup; bloquea todas las historias
- **US1 (Phase 3)**: depende de Foundational
- **US2 (Phase 4)**: depende de Foundational; sus tests usan usuarios autenticados (fábricas de
  conftest), así que se puede hacer en paralelo con US1 en backend; la pantalla necesita login
- **US3 (Phase 5)**: depende de US2 (necesita pisos)
- **US4 (Phase 6)**: depende de US2; independiente de US3 en backend
- **US5 (Phase 7)**: depende de US2; para el borrado de avisos al salir, de US4
- **Polish (Phase 8)**: depende de todas las historias

### Within Each User Story

- Tests primero, y deben fallar
- Esquemas → servicios → routers → pantallas
- Historia completa y en verde antes de pasar a la siguiente prioridad

### Parallel Opportunities

- T003–T006 y T008 en paralelo tras T001–T002
- T011, T013, T015 en paralelo; T018–T023 en paralelo cuando exista conftest
- Dentro de cada historia, todos los tests [P] a la vez y los esquemas en paralelo con las
  pantallas

---

## Parallel Example: User Story 4

```bash
# Tests a la vez:
Task: "T042 Tests de POST/GET /api/avisos en backend/tests/test_avisos.py"
Task: "T043 Tests de DELETE /api/avisos/{id} en backend/tests/test_avisos.py"
Task: "T044 Tests del tablón en frontend/src/__tests__/tablon.test.jsx"

# Después, en paralelo:
Task: "T045 Esquemas en backend/app/schemas/aviso.py"
Task: "T048 Componentes Tablon y AvisoItem en frontend/src/components/"
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Phase 1 Setup → Phase 2 Foundational
2. US1 (cuentas) → validar
3. US2 (pisos) → validar: ya hay una app usable para formar el grupo

### Incremental Delivery

1. + US3 (ver piso) → demo
2. + US4 (tablón) → demo: valor principal de la app
3. + US5 (gestión de miembros) → demo
4. Polish → definición de terminado de SPECS.md §7

### Siguiente feature

El módulo de gastos (SPECS.md §3) va en una feature aparte (`002-gastos-compartidos`) con su
propio `/speckit-specify`, cuando este núcleo esté terminado y en verde.

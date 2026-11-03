# Proceso con Spec Kit

Registro de los pasos seguidos para preparar Convive con
[Spec Kit](https://github.com/github/spec-kit) (Spec-Driven Development) y Claude Code.

**Fecha**: 2026-11-03 · **Spec Kit**: 1.2.7.dev0 · **Agente**: Claude Code (extensión de VS Code)

## Punto de partida

El proyecto solo tenía `SPECS.md`, un documento ordenado como el flujo de Spec Kit:
constitución → especificación → aclaraciones → plan → tareas.

## Paso 1 · Instalar Spec Kit en el proyecto

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init \
  --here --integration claude --script sh --force --non-interactive --ignore-agent-tools
```

- `--here`: inicializa en la carpeta actual en lugar de crear una nueva.
- `--integration claude`: instala los comandos para Claude Code.
- `--script sh`: scripts en bash (Linux).
- `--ignore-agent-tools`: se omite la comprobación del ejecutable `claude`, porque se usa la
  extensión de VS Code y no la CLI.

Notas:

- La opción antigua `--ai claude` ya no existe; ahora es `--integration claude`.
- En esta versión los comandos llevan guion: `/speckit-specify`, no `/speckit.specify`.

Resultado:

- `.specify/`: plantillas, scripts bash, workflow y la constitución (`memory/constitution.md`).
- `.claude/skills/`: los comandos `speckit-constitution`, `speckit-specify`, `speckit-clarify`,
  `speckit-plan`, `speckit-tasks`, `speckit-analyze`, `speckit-checklist`, `speckit-implement`,
  `speckit-converge`.

## Paso 2 · Repositorio git

- `git init -b main`.
- `.gitignore`: se ignora todo `.claude/` salvo `.claude/skills/` (los comandos de Spec Kit se
  versionan), y además `.env`, bases de datos SQLite, `node_modules/`, `dist/` y cachés de
  Python.
- Commit inicial: `docs: ratify constitution v1.0.0 and set up Spec Kit`.
- Rama de la feature: `001-nucleo-convive`.

## Paso 3 · Constitución (`/speckit-constitution`)

Fuente: secciones 0 y 1 de SPECS.md. Fichero: `.specify/memory/constitution.md`, **v1.0.0**.

| Principio | Resumen |
| --- | --- |
| I. Arquitectura API REST + SPA | API JSON bajo `/api`, `backend/` + `frontend/`, cliente API único |
| II. Pila tecnológica fijada | Python 3.12, FastAPI, SQLAlchemy, Alembic, SQLite, React 19, Vite, React Router |
| III. Tests obligatorios | Caso feliz y errores de cada endpoint; tareas solo terminan en verde |
| IV. Seguridad y aislamiento | Hash de contraseñas, token en todo salvo registro/login, solo datos del propio piso |
| V. Contratos consistentes | Formato único de error; dinero en céntimos enteros; euros |
| VI. Código limpio y spec viva | Lógica en servicios; spec y código siempre sincronizados |

Más las secciones *Despliegue y configuración*, *Flujo de desarrollo* y *Governance*
(enmiendas con versionado SemVer).

## Paso 4 · Especificación (`/speckit-specify`)

Fuente: sección 2 de SPECS.md + aclaraciones de la sección 4.
Fichero: `specs/001-nucleo-convive/spec.md`. Puntero activo en `.specify/feature.json`.

Las 11 historias de SPECS.md se agruparon en 5 historias priorizadas e independientes:

| Historia | Prioridad | HU de SPECS.md |
| --- | --- | --- |
| US1 Crear cuenta e iniciar sesión | P1 (MVP) | HU-01, HU-02 |
| US2 Crear un piso o unirse a uno | P1 (MVP) | HU-03, HU-04 |
| US3 Ver mi piso | P2 | HU-05 |
| US4 Tablón de avisos | P2 | HU-09, HU-10, HU-11 |
| US5 Gestionar los miembros del piso | P3 | HU-06, HU-07, HU-08 |

Incluye 24 requisitos funcionales, casos límite, entidades y 6 criterios de éxito medibles.
El checklist de calidad (`checklists/requirements.md`) pasó entero a la primera.

## Paso 5 · Aclaraciones (`/speckit-clarify`)

Se detectaron cuatro huecos que SPECS.md no resolvía:

| Pregunta | Respuesta |
| --- | --- |
| ¿Se pide nombre visible al registrarse? | Sí, obligatorio (1–40 caracteres) |
| ¿Cuánto dura la sesión? | 24 horas, sin renovación |
| ¿Qué pasa con los avisos de quien abandona o es expulsado? | **Se borran** todos sus avisos de ese piso |
| ¿Idioma de la interfaz? | **Español e inglés**, español por defecto |

Las respuestas se integraron en `spec.md` (sección *Clarifications* y requisitos afectados) y
también en `docs/SPECS.md` (§2.3, §4, §5.2 y §5.3), para que no diverjan.

## Paso 6 · Plan (`/speckit-plan`)

Ficheros en `specs/001-nucleo-convive/`:

- `plan.md`: contexto técnico, comprobación de la constitución (todo ✅) y estructura de
  carpetas.
- `research.md`: decisiones técnicas. Las principales:
  - Argon2id para contraseñas; JWT HS256 de 24 h.
  - Login sin enumeración de emails (verificación contra un hash ficticio).
  - Manejadores globales de error; la validación de FastAPI pasa de 422 a 400.
  - i18n propio sin librería: `Accept-Language` en backend; diccionarios y contexto en frontend.
  - SQLAlchemy síncrono, `PRAGMA foreign_keys=ON`, Alembic al arrancar el contenedor.
  - Docker: `python:3.12-slim` y `node:22` → `nginx:alpine`, puerto 5173 en el host.
- `data-model.md`: tablas, restricciones, transiciones de estado y validaciones.
- `contracts/api.md`: los 12 endpoints con todos sus errores y el catálogo de mensajes es/en.
  Se añadió `GET /api/auth/yo`, que el frontend necesita para decidir entre `/bienvenida` y
  `/piso`.
- `quickstart.md`: arranque, tests y recorrido manual de las historias.

## Paso 7 · Tareas (`/speckit-tasks`)

Fichero: `specs/001-nucleo-convive/tasks.md`, con **60 tareas** (T001–T060):

| Fase | Tareas |
| --- | --- |
| 1 Setup (estructura, dependencias, Docker, README) | T001–T008 |
| 2 Base (BD, modelos, migración, errores, i18n, seguridad, cliente API, rutas protegidas) | T009–T023 |
| 3 US1 Cuentas 🎯 MVP | T024–T030 |
| 4 US2 Pisos | T031–T037 |
| 5 US3 Ver piso | T038–T041 |
| 6 US4 Tablón | T042–T048 |
| 7 US5 Gestión de miembros | T049–T055 |
| 8 Pulido (aislamiento, trazabilidad, quickstart, docs) | T056–T060 |

En cada historia los tests van primero. Las tareas marcadas `[P]` se pueden hacer en paralelo.

## Paso 8 · Revisión de consistencia (análisis)

Se revisaron spec, plan y tareas entre sí:

- Cada requisito funcional (FR-001…FR-024) tiene al menos una tarea, y cada criterio de
  aceptación un test.
- SC-001 y SC-002 (tiempos de registro y unión) se validan a mano con el quickstart (T059).
- Diferencias con SPECS.md original, ya reflejadas en `docs/SPECS.md`: nombre obligatorio,
  sesión de 24 h, borrado de avisos al salir, interfaz bilingüe y endpoint `GET /api/auth/yo`.

## Paso 9 · Implementación (`/speckit-implement`)

Se ejecutaron las 60 tareas de `tasks.md` por fases, con los tests antes del código, y todas están
marcadas `[X]`.

**Backend** (`backend/`):

- `core/`: configuración por variables de entorno, BD con claves foráneas, formato único de error
  (también 422 → 400, 404, 405 y 500), mensajes es/en según `Accept-Language`, Argon2id y JWT de 24 h.
- `models/` + migración Alembic `0001_nucleo` (un test comprueba que coincide con los modelos).
- `services/`: toda la lógica (registro sin enumeración de emails, código de invitación único,
  traspaso de administrador al más antiguo, borrado de avisos al salir, aislamiento por piso).
- `routers/`: 12 endpoints finos, sin lógica de negocio.
- **95 tests** con pytest, todos en verde.

**Frontend** (`frontend/`):

- Cliente único `src/api/client.js` (token, idioma, errores y cierre de sesión ante 401).
- `AuthContext` (token en memoria y `localStorage`), `LangContext` (es/en recordado), rutas
  protegidas y pantallas Login, Registro, Bienvenida y Piso (miembros, código, tablón).
- Formularios con `useActionState` de React 19 y confirmación dentro de la página antes de
  expulsar, abandonar o regenerar el código.
- **36 tests** con Vitest y React Testing Library, todos en verde.

**Docker**: `docker compose up --build` levanta `backend` (8000) y `frontend` (Nginx en 5173,
con proxy de `/api`). Se validó el quickstart de principio a fin con peticiones reales, incluida
la persistencia tras `docker compose down` y `up`.

**Trazabilidad**: `specs/001-nucleo-convive/checklists/trazabilidad.md` relaciona cada criterio
de aceptación con sus tests.

Ajustes durante la implementación (ya reflejados en los artefactos):

- React Router en modo declarativo (`<Routes>`) en lugar de `createBrowserRouter`, para poder
  probar con `<MemoryRouter>`.
- El comando de tests del frontend en Docker monta `node_modules` en un volumen aparte para no
  sobrescribir el de la máquina local.

## Siguientes pasos

1. El núcleo ya está en verde: la siguiente feature es el módulo de gastos
   (SPECS.md §3), con `/speckit-specify`, que creará `specs/002-gastos-compartidos/`.

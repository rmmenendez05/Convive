# Implementation Plan: Núcleo de Convive (cuentas, pisos y tablón)

**Branch**: `001-nucleo-convive` | **Date**: 2026-11-03 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-nucleo-convive/spec.md`

## Summary

Aplicación web para compañeros de piso: registro e inicio de sesión, creación de un piso con
código de invitación, unión con código, gestión de miembros (expulsar, abandonar, traspaso de
administrador, regenerar código) y un tablón de avisos. Backend FastAPI + SQLAlchemy sobre
SQLite con migraciones Alembic, expuesto como API REST JSON bajo `/api`; frontend React 19 + Vite
servido por Nginx, que hace de proxy de `/api`. Todo se levanta con `docker compose up --build`.
Interfaz y mensajes de error en español e inglés.

## Technical Context

**Language/Version**: Python 3.12 (backend); JavaScript ES2022 con Node 22 LTS solo para compilar
(frontend)

**Primary Dependencies**: FastAPI, SQLAlchemy 2.x (modo síncrono), Alembic, Pydantic v2 +
email-validator, PyJWT, argon2-cffi, Uvicorn · React 19, React Router 7, Vite

**Storage**: SQLite en un volumen Docker (`/data/convive.db`), claves foráneas activadas

**Testing**: pytest + httpx (`TestClient`) en backend; Vitest + React Testing Library + jsdom en
frontend

**Target Platform**: Contenedores Linux (`python:3.12-slim`, `nginx:alpine`); navegador de
escritorio y móvil modernos

**Project Type**: Aplicación web (backend API + frontend SPA)

**Performance Goals**: Uso doméstico; respuestas percibidas como inmediatas (< 300 ms en local)

**Constraints**: Importes futuros en céntimos enteros; formato de error único; sin secretos en
el código; arranque solo con Docker

**Scale/Scope**: Decenas de usuarios, pisos de 2–10 miembros, cientos de avisos; 11 historias de
usuario, 12 endpoints, 4 pantallas

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cómo se cumple | Estado |
| --- | --- | --- |
| I. API REST + SPA | API JSON bajo `/api`; SPA React; carpetas `backend/` y `frontend/`; cliente único en `frontend/src/api/client.js` | ✅ |
| II. Pila fijada | FastAPI, SQLAlchemy, Alembic, SQLite, React 19, Vite, React Router; versiones exactas en `requirements.txt` y `package-lock.json` | ✅ |
| III. Tests obligatorios | Cada endpoint con test de caso feliz y de cada error de [contracts/api.md](./contracts/api.md); tests de pantallas con RTL | ✅ |
| IV. Seguridad y aislamiento | Argon2 para contraseñas; JWT de 24 h en todo salvo registro/login; todas las consultas filtran por el piso del usuario autenticado | ✅ |
| V. Errores y dinero | Manejadores globales que convierten toda excepción (incluida la validación de Pydantic, 422 → 400) al formato `{error:{code,message}}`; sin importes en este núcleo | ✅ |
| VI. Código limpio, spec viva | Routers finos → servicios con la lógica; SPECS.md (en `docs/`) actualizado con las aclaraciones | ✅ |
| Despliegue | `docker-compose.yml` con `backend` (8000) y `frontend` (Nginx, 80 → host 5173), volumen `convive-data`, `.env.example` | ✅ |

**Post-design re-check (tras Phase 1)**: ✅ sin violaciones. Las únicas decisiones añadidas
(i18n propio sin librería, borrado de avisos al salir) no contradicen ningún principio.

## Project Structure

### Documentation (this feature)

```text
specs/001-nucleo-convive/
├── plan.md              # Este fichero
├── research.md          # Phase 0: decisiones técnicas
├── data-model.md        # Phase 1: entidades, reglas e índices
├── quickstart.md        # Phase 1: cómo arrancar y validar
├── contracts/
│   └── api.md           # Phase 1: contrato REST con todos los errores
├── checklists/
│   └── requirements.md  # Calidad de la spec
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
docker-compose.yml
.env.example
README.md
backend/
├── Dockerfile
├── requirements.txt
├── alembic.ini
├── alembic/
│   └── versions/            # 0001_nucleo.py
├── app/
│   ├── main.py              # crea la app, registra routers y manejadores de error
│   ├── core/                # config.py, db.py, security.py, errors.py, i18n.py
│   ├── models/              # usuario.py, piso.py, miembro.py, aviso.py
│   ├── schemas/             # auth.py, piso.py, aviso.py (Pydantic)
│   ├── routers/             # auth.py, pisos.py, avisos.py (solo HTTP)
│   ├── services/            # auth_service.py, piso_service.py, aviso_service.py
│   └── deps.py              # get_db, get_usuario_actual, get_miembro_actual
└── tests/
    ├── conftest.py          # BD SQLite en memoria por test, cliente y fábricas
    ├── test_auth.py
    ├── test_pisos.py
    ├── test_miembros.py
    ├── test_avisos.py
    └── test_errores.py
frontend/
├── Dockerfile               # etapa node:22 → etapa nginx:alpine
├── nginx.conf               # SPA fallback + proxy /api → backend:8000
├── package.json
├── vite.config.js           # proxy /api en dev + config de Vitest
└── src/
    ├── main.jsx, App.jsx    # router y rutas protegidas
    ├── api/client.js        # único módulo que llama a la API
    ├── context/             # AuthContext.jsx, LangContext.jsx
    ├── i18n/                # es.js, en.js, useT.js
    ├── components/          # RutaProtegida, FormError, SelectorIdioma, AvisoItem…
    ├── pages/               # Login, Registro, Bienvenida, Piso
    └── __tests__/           # tests Vitest + RTL
```

**Structure Decision**: Aplicación web con `backend/` y `frontend/` (constitución I), siguiendo
la estructura de SPECS.md §5.4 y añadiendo `core/` para piezas transversales y `i18n/` para los
textos bilingües.

## Complexity Tracking

Sin violaciones de la constitución; no aplica.

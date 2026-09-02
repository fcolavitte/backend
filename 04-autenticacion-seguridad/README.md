# 🚀 Módulo 04 — Autenticación y Seguridad

> **Empezá acá.** Este documento te dice qué es este módulo, cómo arrancar y
> dónde está cada cosa. Después seguí con `GUIA_ALUMNO.md`.

---

## ¿De qué se trata?

En el Módulo 03 reorganizaste la API de tareas en **capas**. Pero seguía de
**puertas abiertas**: cualquiera podía listar, crear, editar y borrar. Hoy
vas a **cerrar la puerta**:

- **Registro de usuarios** (`register`) → contraseña hasheada con **Argon2**
- **Login** → verificación + emisión de un **JWT**
- **Endpoint protegido** (`/api/users/me`) → solo con token válido
- **Frontend React + TypeScript** → cierra el ciclo: register, login y perfil desde la UI

Y vas a entender **por qué** cada pieza existe: qué es una sesión, qué es un
JWT, por qué SSO y JWT no se comparan, y qué amenazas de OWASP te tocan.

---

## Cómo empezar (fork → clonar → desarrollar)

### 1. Hacé un fork del repositorio

En GitHub, andá al repo de la materia y clickeá **Fork**. Esto te crea una
**copia propia** donde trabajás sin miedo a romper nada.

### 2. Cloná TU fork

```bash
git clone https://github.com/TU_USUARIO/backend.git
cd backend/04-autenticacion-seguridad
```

### 3. Leé el material previo (si no lo hiciste)

Abrí [`MATERIAL_PREVIO.md`](./MATERIAL_PREVIO.md). Ahí están los conceptos
(hash, sesión vs JWT, SSO vs JWT, OWASP) + la **bibliografía extensa** de
cada tema. Sin esto, el taller va a ser cuesta arriba.

### 4. Entendé qué vas a construir

Leé [`SPEC.md`](./SPEC.md) — es tu **recurso de aprendizaje**: qué construís,
por qué, y qué vas a descubrir en el camino.

### 5. Desarrollá el backend (las 6 piezas)

Seguí [`GUIA_ALUMNO.md`](./GUIA_ALUMNO.md). Completás **6 archivos**:

| Archivo | Responsabilidad |
|---------|-----------------|
| `backend/app/security.py` | hash Argon2 + JWT |
| `backend/app/repositories/user_repository.py` | acceso a datos |
| `backend/app/services/auth_service.py` | register + login (negocio) |
| `backend/app/dependencies.py` | `get_current_user` (protege rutas) |
| `backend/app/controllers/auth_controller.py` | endpoints register/login |
| `backend/app/controllers/users_controller.py` | endpoint `/me` |

### 6. Conectá el frontend

El frontend ya viene **completo** (`frontend/`). Solo lo levantás y verificás
el ciclo completo desde la UI: registrarte → loguearte → ver tu perfil.

### 7. Verificá con Postman

Importá la collection de `postman/` y corré el flujo feliz + casos límite.

---

## Qué está completo y qué tenés que completar

| Componente | Estado |
|-----------|--------|
| `backend/app/models/user.py` | ✅ Dado (modelo + schemas) |
| `backend/app/config.py` | ✅ Dado (SECRET_KEY, expiración) |
| `backend/app/database.py` | ✅ Dado (engine + session) |
| `backend/app/main.py` | ✅ Dado (entrypoint) |
| `backend/app/controllers/health_controller.py` | ✅ Dado (**ejemplo vivo**) |
| `backend/app/security.py` | 🔓 **Completás vos** |
| `backend/app/repositories/user_repository.py` | 🔓 **Completás vos** |
| `backend/app/services/auth_service.py` | 🔓 **Completás vos** |
| `backend/app/dependencies.py` | 🔓 **Completás vos** (solo `get_current_user`) |
| `backend/app/controllers/auth_controller.py` | 🔓 **Completás vos** |
| `backend/app/controllers/users_controller.py` | 🔓 **Completás vos** |
| `frontend/` | ✅ Dado (completo, se conecta al final) |

---

## Estructura del repo

```
04-autenticacion-seguridad/
├── README.md            # este archivo — empezá acá
├── SPEC.md              # recurso de aprendizaje (qué + por qué)
├── MATERIAL_PREVIO.md   # lectura pre-clase + bibliografía extensa
├── GUIA_ALUMNO.md       # guía de descubrimiento paso a paso
├── PRESENTACION.md      # material del docente (Marp)
├── backend/
│   ├── app/             # las capas + security (6 archivos para completar)
│   ├── pyproject.toml   # dependencias (uv): pwdlib[argon2], pyjwt
│   └── .env.example     # plantilla de configuración
├── frontend/            # React + Vite + TypeScript (dado)
└── postman/             # collection con tests
```

---

## Levantar el backend

```bash
cd backend
cp .env.example .env        # completá DATABASE_URL + SECRET_KEY
uv sync                     # instala pwdlib[argon2], pyjwt, email-validator
uv run -m app.main          # http://localhost:8000
```

> La tabla `users` se crea sola al arrancar (`create_all`). La base es la
> misma de los módulos anteriores; la tabla `tasks` no se toca.

## Levantar el frontend

```bash
cd frontend
pnpm install
pnpm dev                    # http://localhost:5173 (proxy → :8000)
```

> El frontend viene **completo**. Hacé el ciclo desde la UI: registrate,
> logueate y mirá tu perfil. El token se guarda en `localStorage` y viaja en
> el header `Authorization: Bearer`.

---

## Regla de oro del taller

> **No busques la solución. Descubrila.** Cuando te trabes, preguntate:
> *"¿esto es HTTP, negocio, datos, o criptografía?"*. Esa pregunta destraba
> el 90% de las dudas.

*"La Universidad te da el mapa. El recorrido lo hacés vos."*

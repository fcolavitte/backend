# 📘 SPEC — Módulo 06: Autorización RBAC (entrega obligatoria)

> **Entrega obligatoria** para la materia Desarrollo de Software 2026.
> **Fecha límite**: martes 22 de septiembre de 2026.
> **Modalidad**: fork del repo de la cátedra, trabajo individual, defensa oral.

---

## 1 · Qué construís

Sobre el backend del Módulo 05 (7 métodos de autenticación + JWT), agregás la
**capa de AUTORIZACIÓN** con autorización:

- **3 dependencias reutilizables**: `get_current_user` (ya hecho), `require_role`,
  `require_scope`.
- **6 endpoints de documentos** protegidos: CRUD + publicación.
- **3 endpoints de usuarios** protegidos: solo admin de la empresa puede verlos.
- **Multi-tenancy**: 2 empresas demo; cada una ve solo la suya.
- **Object-level access control**: un editor no ve el documento privado de otro (IDOR mitigado).
- **Scopes en el JWT**: el scope del token limita qué puede hacer este token.

### Para qué lo construís (la lección)

Cuando termines, podrás explicar **con tu propio código**:
- Por qué `viewer@acme.com` recibe 403 al intentar ver el documento #2 de `admin@acme.com`.
- Por qué el idem admin logueado con scope `"read"` recibe 403 al crear documento.
- Por qué un admin de Globex no puede ver los usuarios de Acme aunque sea admin.

---

## 2 · Qué te dan (y qué NO modificás)

El repo ya trae el backend casi listo. Solo modificás **4 archivos**:

```
06-autorizacion-rbac/backend/app/
├── models.py            ✅ Dado: Role, User, Document, LoginBody, DocumentCreate...
├── db.py                ✅ Dado: engine + tablas SQLModel (PostgreSQL, persistencia)
├── storage.py           ✅ Dado: seed idempotente (2 tenants + 4 users + 5 docs)
├── config.py            ✅ Dado: SECRET_KEY fail-loud, ALGORITHM
├── security.py          ✅ Dado: hash Argon2 + JWT con claims role/tenant/scope
├── auth_common.py       ✅ Dado: verify_login (con timing attack)
├── auth_controller.py   ✅ Dado: register + login (con scope)
├── dependencies.py      🔓 COMPLETÁS: require_role + require_scope
├── controllers/
│   ├── users_controller.py     🔓 COMPLETÁS: 3 endpoints
│   └── documents_controller.py 🔓 COMPLETÁS: 6 endpoints
└── main.py              ✅ Dado
```

Y **1 archivo del frontend** (React + TypeScript + Vite, la herramienta visual):

```
06-autorizacion-rbac/frontend/src/
└── authz.ts             🔓 COMPLETÁS: 6 helpers de autorización en la UI
```

---

## 3 · La spec de tu entrega (qué tienen que hacer los 4 archivos)

### 3.1 `dependencies.py` — las dependencias de autorización

| Dependencia | Estado | Qué hace |
|-------------|--------|----------|
| `get_current_user` | ✅ Ya resuelto | Decodifica el JWT (401 si inválido). Guarda el payload en `request.state`. |
| `require_role(rol)` | 🔓 Completás | 403 si `current_user.role != rol`. Relee el rol de storage en CADA request. |
| `require_scope(scope)` | 🔓 Completás | 403 si `scope` no está en el claim `scope` del token. |

**Regla de diseño**: el rol se relee de `storage` (el cambio es inmediato). El scope
se lee del `token_payload` (lo fijó el login; es del TOKEN, no del usuario).

### 3.2 `users_controller.py` — gestión de usuarios

| Endpoint | Protección | Qué debe devolver |
|----------|------------|-------------------|
| `GET /api/users` | `require_role("admin")` | Lista los usuarios de TU empresa |
| `GET /api/users/{id}` | `require_role("admin")` + tenancy | 200 si el user es de tu empresa; **403 si es de otra** |
| `PATCH /api/users/{id}/role` | `require_role("admin")` + tenancy | Cambia el rol; 403 si cross-tenant |

### 3.3 `documents_controller.py` — el recurso protegido

| Endpoint | Protección | Qué debe devolver |
|----------|------------|-------------------|
| `POST /api/documents` | `require_scope("write")` | Crea un draft privado (201) |
| `GET /api/documents` | solo autenticado | Públicos del tenant + los tuyos (ya lo hace storage) |
| `GET /api/documents/{id}` | **tenancy + object-level** | Ver tabla de abajo |
| `PATCH /api/documents/{id}` | `require_scope("write")` + dueño o admin + tenancy | Edita (403 si cross-tenant o no eres dueño/admin) |
| `DELETE /api/documents/{id}` | `require_role("admin")` + `require_scope("write")` + tenancy | Borra (403 si cross-tenant) |
| `POST /api/documents/{id}/publish` | `require_scope("write")` + dueño o admin + tenancy | Publica (403 si cross-tenant o no eres dueño/admin) |

**Tabla de `GET /documents/{id}`** (object-level):

| Caso del documento | admin | editor | viewer |
|---------------------|:-----:|:------:|:------:|
| No existe (id inválido) | 404 | 404 | 404 |
| **De OTRA empresa** | **403** | **403** | **403** |
| Público, mismo tenant | 200 ✅ | 200 ✅ | 200 ✅ |
| Privado, propio | 200 ✅ | 200 ✅ | 200 (es tuyo) |
| Privado de OTRO | 200 ✅ | 403 ❌ | 403 ❌ |

### 3.4 `frontend/src/authz.ts` — la autorización en la INTERFAZ

El frontend es una **herramienta de prueba** del backend: viene casi completo
(login con 1 click, probador de la matriz, CRUD visual, consola de requests)
y solo completás **1 archivo**: los helpers que la UI usa para mostrar u
ocultar cada acción según la matriz.

| Helper | Firma | Qué debe devolver (matriz) |
|--------|-------|---------------------------|
| `scopeAllowsWrite` | `(scope: string \| undefined) => boolean` | `true` solo si el scope del TOKEN contiene `"write"` |
| `canManageUsers` | `(role: Role \| undefined) => boolean` | `true` solo para `"admin"` |
| `canChangeRole` | `(role: Role \| undefined) => boolean` | `true` solo para `"admin"` |
| `canDelete` | `(role: Role \| undefined) => boolean` | `true` solo para `"admin"` |
| `canEdit` | `(userId, doc, role) => boolean` | `true` si `doc.owner_id === userId` **o** `role` es admin |
| `canPublish` | `(userId, doc, role) => boolean` | `true` si `doc.owner_id === userId` **o** `role` es admin |

**Regla de oro**: cada helper debe devolver lo que la **matriz del server**
(SECCIONES 3.1-3.3) responde. La UI y el server tienen que quedar ALINEADOS:
si la UI te muestra BORRAR pero el server responde 403, tu helper está roto
(todavía devuelve `true`). Si la UI te oculta el botón pero el server
responde 200, tu backend está roto. **La consola de requests lo hace
visible.**

> ⚠️ **Lección central**: ocultar un botón NO es seguridad. Estos helpers
> son UX honesta — la seguridad REAL la decidís en el server. Si el server
> está vulnerable (dependencies.py sin completar), la UI "dice que sí" y el
> server (roto) también responde 200. Esa inconsistencia en vivo es EXACTAMENTE
> lo que estás arreglando en este módulo.

---

## 4 · Dataset demo (no lo modifiqués)

Los usuarios y documentos PERSISTEN en **PostgreSQL** (service `postgres` del
compose, volumen `pgdata`). El `storage.py` viene con este dataset SEED que se
siembra **SOLO la primera vez** (seed idempotente: si la DB ya tiene datos, no
duplica) — las verificaciones automáticas se basan en él. **No renombres
emails ni documentos** (podés agregar más).

### Empresas (tenants)

| ID | Nombre |
|----|--------|
| 1 | Acme Corp |
| 2 | Globex Inc |

### Usuarios (password: `demo12345`)

| Email | Rol | Tenant |
|-------|-----|--------|
| `admin@acme.com` | admin | Acme (1) |
| `editor@acme.com` | editor | Acme (1) |
| `viewer@acme.com` | viewer | Acme (1) |
| `admin@globex.com` | admin | Globex (2) |

### Documentos

| ID | Título | Owner | Visibilidad | Publicado | Tenant |
|----|--------|-------|-------------|-----------|--------|
| 1 | Manual de bienvenida | admin acme | público | ✅ sí | Acme |
| 2 | Estrategia 2026 | admin acme | privado | ❌ no (draft) | Acme |
| 3 | Notas de reunión | editor acme | privado | ❌ no (draft) | Acme |
| 4 | Informe público Q3 | editor acme | público | ✅ sí | Acme |
| 5 | Plan secreto Globex | admin globex | privado | ❌ no | Globex |

---

## 5 · Herramientas y entorno

### 5.1 Portabilidad: Docker Compose (requerido en la entrega)

Para asegurar que el entorno funcione **igual en cualquier máquina**, la
entrega de este módulo incorpora **Docker + Docker Compose** como requisito
de portabilidad:

> **Tu entrega (los 4 archivos 🔓) debe levantar y pasar los 44 checks
> con el entorno de docker del repo.** La portabilidad es parte de la
> nota: si la cátedra no puede levantar tu fork con `docker compose up`,
> la corrección se hace contra el entorno local de la cátedra (y si ahí
> también falla, es A01: tu entrega no es reproducible).

El repo ya trae la infraestructura lista — **no la modificás**:

```
06-autorizacion-rbac/
├── docker-compose.yml       ✅ Dado (define postgres + backend + frontend como servicios)
├── backend/Dockerfile       ✅ Dado (python:3.12-slim + uv + uvicorn +0.0.0.0)
├── backend/uv.lock          ✅ Dado (dependencias Python congeladas por uv)
├── backend/.dockerignore    ✅ Dado (excluye .venv, caches)
├── frontend/Dockerfile      ✅ Dado (node:22-alpine + pnpm/corepack + vite dev +0.0.0.0)
└── frontend/.dockerignore   ✅ Dado (excluye node_modules, dist)
```

**Levantar todo el entorno con un solo comando:**

```bash
# desde la raíz del módulo 06-autorizacion-rbac/
docker compose up --build

# postgres → localhost:5432   (persistencia, volumen pgdata)
# backend  → http://localhost:8000
# frontend → http://localhost:5173
```

El `docker-compose.yml`:

- **postgres**: PostgreSQL 16 con healthcheck (`pg_isready`) y el volumen
  `pgdata` — la persistencia real. El backend espera a que esté SANO.
- **backend**: build con el `Dockerfile`, expone `8000:8000`, corre con
  `ENVIRONMENT=development` y `DATABASE_URL` apuntando al service `postgres`
  (config.py usa defaults de dev) y tiene healthcheck sobre `/api/health` —
  el frontend espera a que esté sano.
- **frontend**: build con el suyo, expone `5173:5173`, y el proxy `/api`
  apunta a `http://backend:8000` (el nombre del service en la red interna
  de Compose, no `localhost`).

> 💡 **Reiniciar no borra nada**: los datos viven en el volumen `pgdata`.
> Para devolver la DB a su estado inicial (volver a sembrar el seed tenés
> que borrar el volumen a propósito): `docker compose down -v`.

**Verificar tu trabajo (igual que sin docker, desde el host):**

```bash
bash scripts/verificar_authz.sh
# → 44 checkpoints: todos ✅ = tu entrega está lista
```

El script pega sobre `http://127.0.0.1:8000`, que es justo el puerto que
expone el contenedor → **el flujo de verificación no cambia en nada.**

> 💡 **Por qué portabilidad**: "funciona en mi máquina" no es una entrega.
> Docker Compose declara el entorno ENTERO (lenguaje, dependencias, puertos)
> en un archivo versionable. Si corre acá, corre igual en el aula, en el
> home del corrector o en CI. Ese es el estándar 2026 de cualquier lab.

### Requisitos

| Herramienta | Para qué | Verificar |
|-------------|----------|-----------|
| **Docker Engine** (≥ 24) | contenedores de backend y frontend | `docker --version` |
| **Docker Compose v2** | orquestar los servicios | `docker compose version` |
| **uv** (≥ 0.5) | toolchain Python: tu dev local Y el contenedor del backend | `uv --version` |
| **pnpm** (≥ 9) | toolchain Node: tu dev local Y el contenedor del frontend | `pnpm --version` |
| Python ≥ 3.12 | runtime del backend (lo maneja uv) | `python3 --version` |
| **bash** | script de verificación (siempre) | `bash --version` |

> **PostgreSQL NO se instala local**: corre como service del compose
> (imagen `postgres:16-alpine`, volumen `pgdata`). Para desarrollo local
> con `uv` lo levantás primero con `docker compose up -d postgres` (o apuntás
> `DATABASE_URL` a cualquier PostgreSQL que tengas).
>
> La toolchain es SIEMPRE la misma, adentro y afuera del contenedor: **uv**
> dentro de la imagen del backend y **pnpm** (vía corepack) dentro de la del
> frontend — exactamente lo que corre en tu máquina con `uv sync` y
> `pnpm install`. El lockfile (`uv.lock` / `pnpm-lock.yaml`) congela las
> versiones: lo que levanta `docker compose up --build` es idéntico a tu
> entorno local. Esa es la portabilidad: docker no cambia las herramientas,
> docker empaqueta las mismas.

### Arrancar el backend (desarrollo local)

```bash
# 1) La base de datos (service postgres del compose; puerto 5432 expuesto)
docker compose up -d postgres

# 2) El backend con uv — apunta al mismo postgres (localhost:5432)
cd 06-autorizacion-rbac/backend
uv sync               # crea .venv con las dependencias (incluye sqlmodel + psycopg)
uv run -m app.main    # arranca en http://127.0.0.1:8000
```

El dataset se siembra SOLO la primera vez (persistencia: sobrevive a
reinicios; duplicarlo no es tu trabajo).

### Arrancar el frontend (desarrollo local)

En **otra terminal** (el backend sigue corriendo en :8000):

```bash
cd 06-autorizacion-rbac/frontend
pnpm install
pnpm dev                    # → http://localhost:5173
```

La interfaz te muestra los 4 usuarios demo con un click, el probador de
la matriz por ID, el CRUD de documentos y la consola de requests. Mirá el
`README.md` de esta carpeta para más detalles.

### Verificar tu trabajo

```bash
bash scripts/verificar_authz.sh
# → 44 checkpoints: todos ✅ = tu entrega está lista
```

Si algún check falla, el script te dice **cuál** y qué HTTP code esperaba.
Cada check es un CASO DE LA MATRIZ de la sección 3 de esta spec.

---

## 6 · Criterios de evaluación (corrección + defensa oral)

### Lo que evalúa el script (40% de la nota)

Cada check es un caso de la matriz. **44 checks verdes** = aprobado en práctica.
Si algún check falla, descontamos los puntos de cada celda rota.

### Lo que evalúa el código (30% de la nota)

**Backend (20%)** — los 3 archivos de autorización:

| Criterio | Qué miramos |
|----------|------------|
| **Deny-by-default** | Todo endpoint nuevo tiene dependencia de authz |
| **Dependencias reutilizables** | `require_role` y `require_scope` son factories, no código inline |
| **Tenancy en TODOS los endpoints** | No hay endpoint que olvide el filtro por tenant |
| **Object-level en GET** | Mitigación de IDOR: owner o admin en documentos privados |
| **Legibilidad** | Comentarios explicando POR QUÉ el 403, no solo el código |

**Frontend (10%)** — los 6 helpers de `authz.ts`:

| Criterio | Qué miramos |
|----------|------------|
| **Coherencia con la matriz** | Cada helper devuelva lo que la spec define para su celda |
| **Scope en token** | `scopeAllowsWrite` lee el claim del JWT (no confunde con rol) |
| **Owner + admin** | `canEdit` y `canPublish` distinguen dueño vs admin |

### La defensa oral (30% de la nota)

Según el resultado del script de verificación, se programa una defensa oral
individual de **5 minutos** en la próxima clase presencial.

**Qué se evalúa en la defensa oral:**

1. **Demostración en vivo** (1 min): corré el script de verificación y
   mostrá los 44 checks verdes. Si algún check falla, explicá POR QUÉ.

2. **Preguntas conceptuales** (4 min). Ejemplos:
   - "¿Por qué el 403 va después del 404 en `GET /api/documents/{id}`?"
     → Si el id no existe, no hay nada que proteger. Pero en cross-tenant
     el recurso EXISTE — solo que no te corresponde: 403.
   - "¿Por qué el rol se lee de storage y no del token?"
     → Si un admin cambia el rol de alguien, el cambio es inmediato.
     Si leyéramos del token, el usuario viejo seguiría con su rol hasta
     que expire el JWT. Eso es un bug en producción.
   - "¿Qué pasaría si quitás la dependencia `require_role` de `GET /users`?"
     → Deny-by-default roto: cualquier autenticado lista los usuarios.
     Esto es un A01 (Broken Access Control) clásico.
   - "¿Por qué la entrega exige `docker compose up`?"
     → Portabilidad: el entorno es parte del entregable. Declarando
     imágenes, puertos y healthchecks en un YAML versionable, el mismo
     código corre en el aula, en tu casa o en CI sin "acá a mí me anda".

3. **Revisión de código** (proporcional al resultado del script):
   - Si el script pasó con 44/44: revisamos tu implementations de
     `require_role`, `require_scope` y el object-level de documents.
   - Si algún check falló: explicás por qué y proponés el fix.

---

## 7 · Cómo entregar

1. **Fork** del repo base: `https://github.com/desasoftfrlptn/backend.git`
2. Creá una rama con tu nombre: `git checkout -b tu-nombre/06-autorizacion-rbac`
3. Commiteá la carpeta del backend **y** tu `authz.ts` del frontend:
   ```bash
   git add 06-autorizacion-rbac/backend/app/dependencies.py \
           06-autorizacion-rbac/backend/app/controllers/ \
           06-autorizacion-rbac/frontend/src/authz.ts
   ```
4. Hacé push a TU fork
5. Abrí un **Pull Request** al repo base: título `"Entrega Módulo 06 — [Tu Nombre]"`
6. En la descripción del PR pegá la salida de `verificar_authz.sh` (todos los ✅)

> ⚠️ El PR debe estar abierto antes de la fecha límite (22/09 23:59).
> No se reciben entregas por mail ni por otro canal.

---

## 8 · Decisiones de diseño que debés explicar

En la defensa oral vas a tener que justificar **por qué tus decisiones son las correctas**.
Estas son las que el docente espera escuchar:

| Decisión | Por qué |
|----------|---------|
| `401` ≠ `403` | 401 = no autenticado. 403 = autenticado pero sin permiso. |
| Rol en storage, scope en token | El cambio de rol es inmediato; el scope vive con el token. |
| Owner check en documentos privados | Mitiga IDOR (OWASP A01). |
| Tenancy en endpoints de escritura | Un admin de Acme no borra documentos de Globex. |
| `require_role` y `require_scope` como factories | Patrón reutilizable, no código inline en cada endpoint. |
| Deny-by-default | Cualquier endpoint sin dependencia de authz es un bug. |
| Portabilidad (Docker Compose) | El entorno ENTERO se declara en docker-compose.yml (postgres + backend + frontend + volumen + healthchecks). "Funciona en mi máquina" no es una entrega: si tu fork no levanta con `docker compose up`, la corrección no puede empezar. |
| UI como proxy de la matriz | La UI replica la matriz con helpers (`authz.ts`), pero la
| seguridad REAL la decide el server. Si el server está roto, la UI
| "dice que sí" y el server también — el 200 aparece en la consola. |

---

> **Tiempo estimado de la entrega**: 60-90 minutos (si leíste el MATERIAL_PREVIO).
> **La spec de esta entrega reemplaza a cualquier otro material.** Leé esta SPEC
> antes de tocar código. Si algo de esta spec contradice al MATERIAL_PREVIO,
> lo que dice acá es lo que se evalúa.
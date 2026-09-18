# 🚦 Módulo 06 — Autorización RBAC

> **Entrega OBLIGATORIA** · Desarrollo de Software 2026 (UTN)
> **Formato**: aula invertida (lectura previa + trabajo práctico individual)
> **Fecha límite**: martes **22/09/2026** · **Defensa oral**: clase siguiente
> **Entrega**: fork del repo base + PR

---

## ¿De qué se trata?

En los módulos 04 y 05 cerraste la puerta de la **autenticación**: ahora la
API sabe quién sos. Este módulo cierra la segunda puerta — la que la
industria considera **la brecha #1 de seguridad (OWASP A01)**:

> **Autorización**. No alcanza con "estás logueado". Hay que decidir
> **qué PODÉS hacer** con eso.

Construís una **API de documentos** con:

| Pilar | Qué resuelve |
|-------|--------------|
| **RBAC** | Roles `admin`·`editor`·`viewer` con permisos |
| **Object-level** | Un editor no ve el privado de otro (**IDOR mitigado**) |
| **Scopes** | El TOKEN tiene límites propios (read vs read write) |
| **Multi-tenancy** | Cada empresa ve SOLO la suya |
| **Deny-by-default** | Endpoint sin autorización = bug de seguridad |

---

## Cómo arrancar

### 1. Leé ANTES de la clase (aula invertida)

1. [`MATERIAL_PREVIO.md`](./MATERIAL_PREVIO.md) — la lectura pre-clase
   (35-40 min): authN vs authZ, RBAC, IDOR, scopes, tenancy, deny-by-default.
2. [`SPEC.md`](./SPEC.md) — **la spec de la entrega**: qué hacer, con qué
   herramientas, criterios de evaluación y cómo entregar.
3. [`GUIA_ALUMNO.md`](./GUIA_ALUMNO.md) — la guía paso a paso con consignas.

### 2. Trabajo práctico (individual)

Solo tenés que completar **4 archivos** (3 backend + 1 frontend):

| Archivo | Qué completás |
|---------|---------------|
| `backend/app/dependencies.py` | `require_role` + `require_scope` |
| `backend/app/controllers/users_controller.py` | Proteger 3 endpoints (admin + tenancy) |
| `backend/app/controllers/documents_controller.py` | Proteger 6 endpoints (scope + IDOR + tenancy) |
| `frontend/src/authz.ts` | 6 helpers de autorización en la UI (coherentes con la matriz) |

### 3. Levantá y verificá

**Opción A — Docker Compose (la forma de la entrega, portabilidad)** ✅

El repo trae `docker-compose.yml` + los Dockerfiles. Levanta TODO el entorno
(backend + frontend + **postgres** con persistencia) con un solo comando:

```bash
cd 06-autorizacion-rbac
docker compose up --build
# postgres → localhost:5432 (volumen pgdata: los datos sobreviven a reinicios)
# backend  → http://localhost:8000
# frontend → http://localhost:5173
```

**Opción B — local con uv/pnpm** (para desarrollar sin levantar backend y
frontend en docker; **la base de datos sigue viniendo de docker**):

```bash
# Terminal 0 — la DB (service postgres del compose, puerto 5432)
docker compose up -d postgres

# Terminal 1 — backend
cd backend
uv sync
uv run -m app.main                      # → http://127.0.0.1:8000

# Terminal 2 — frontend (herramienta visual para probar la matriz)
cd frontend
pnpm install
pnpm dev                                # → http://localhost:5173
```

En ambas opciones el dataset se siembra SOLO la primera vez (2 empresas,
4 usuarios, 5 docs) y **persiste** entre reinicios del backend.

Verificá (igual con docker o sin docker — el script pega sobre :8000):

```bash
bash scripts/verificar_authz.sh
# → 44 checkpoints: TODOS ✅ = entrega lista
```

Cada check es **un caso de la matriz de autorización**: si un check falla,
sabés exactamente qué caso de abuso dejaste abierto.

### 4. Entregá (fork + PR)

1. Fork del repo: `https://github.com/desasoftfrlptn/backend.git`
2. Rama: `tu-nombre/06-autorizacion-rbac`
3. PR al repo base con la salida del script pegada en la descripción.

> ⚠️ **Fecha límite**: 22/09 23:59. La defensa oral se agenda en la clase
> presencial siguiente según el resultado del script.

---

## Estructura

```
06-autorizacion-rbac/
├── README.md                 # este archivo — empezá acá
├── MATERIAL_PREVIO.md        # lectura pre-clase (aula invertida)
├── SPEC.md                   # ⭐ spec de la entrega (qué/con qué/criterios)
├── GUIA_ALUMNO.md            # guía de descubrimiento por fases
├── docker-compose.yml        # 🐳 portabilidad: levanta backend + frontend
├── backend/
│   ├── app/                  # 3 archivos a completar (🔓)
│   ├── pyproject.toml        # dependencias (uv)
│   ├── Dockerfile            # 🐳 imagen del backend (python:3.12-slim)
│   └── .env.example
├── frontend/
│   ├── src/authz.ts          # 🔓 1 archivo a completar (helpers autorización)
│   ├── Dockerfile            # 🐳 imagen del frontend (node:22-alpine + vite)
│   └── ...                   # todo lo demás dado (herramienta de prueba)
├── postman/
│   └── 06-autorizacion-rbac.postman_collection.json
└── scripts/
    └── verificar_authz.sh    # ✅ corrección automática (44 checks)
```

---

## Endpoints de la API

| Método | Ruta | Protección | Qué hace |
|--------|------|-----------|----------|
| `POST` | `/api/auth/register` | pública | Registra (nace viewer) |
| `POST` | `/api/auth/login` | pública | JWT con role/tenant/scope |
| `GET` | `/api/users` | admin | Usuarios de tu empresa |
| `GET` | `/api/users/{id}` | admin + tenancy | Detalle (403 cross-tenant) |
| `PATCH` | `/api/users/{id}/role` | admin + tenancy | Cambia el rol |
| `POST` | `/api/documents` | scope write | Crea draft privado |
| `GET` | `/api/documents` | autenticado | Públicos + los tuyos |
| `GET` | `/api/documents/{id}` | tenancy + object-level | Ve (IDOR mitigado) |
| `PATCH` | `/api/documents/{id}` | scope write + dueño/admin + tenancy | Edita |
| `DELETE` | `/api/documents/{id}` | admin + scope write + tenancy | Borra |
| `POST` | `/api/documents/{id}/publish` | scope write + dueño/admin + tenancy | Publica |

**Usuarios demo** (password `demo12345`): `admin@acme.com` · `editor@acme.com`
· `viewer@acme.com` · `admin@globex.com`

---

## Buenas prácticas 2026 que reutiliza

1. **Argon2id** para hash (pwdlib) — no bcrypt ni hashlib.
2. **JWT con `algorithms` explícito** e `iss`/`aud` validados cuando aplica.
3. **`SECRET_KEY` fail-loud**: la app NO arranca en producción sin ella.
4. **Timing attack mitigation** en el login (hash señuelo).
5. **403 explícito en autorización** — nunca confundir con 401.
6. **Tenancy en TODO**: filtro por `tenant_id` en cada query.
7. **Deny-by-default**: depende de `require_role`/`require_scope` en cada ruta.

---

> **Único objetivo del módulo**: que entiendas de verdad la diferencia entre
> "el usuario está logueado" y "el usuario puede hacer esto". Esa distinción
> es la que los incidentes de seguridad más caros de la historia no supieron
> hacer. **Ponete las pilas: la defensa oral lo va a notar.**
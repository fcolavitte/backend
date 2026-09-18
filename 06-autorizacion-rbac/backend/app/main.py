"""
Entrypoint del módulo 06 — Autorización RBAC.

Levanta la API de documentos con autorización completa:

    Autenticación (reutilizada del 04/05, NO es la lección):
      POST /api/auth/register   → crea un usuario (siempre viewer)
      POST /api/auth/login      → JWT con claims role/tenant_id/scope

    Autorización (LA LECCIÓN — vos la escribís en dependencies.py y los
    controllers marcados con 🔓 en el README del módulo):
      GET  /api/users            → lista usuarios de TU empresa   (admin)
      GET  /api/users/{id}       → detalle de un usuario de TU empresa (admin)
      PATCH /api/users/{id}/role → cambia el rol (admin de la MISMA empresa)
      POST /api/documents        → crea un documento (draft privado)
      GET  /api/documents        → públicos de tu empresa + los tuyos
      GET  /api/documents/{id}   → objeto: dueño / admin / público (tenancy)
      PATCH /api/documents/{id}  → edita (dueño o admin; scope "write")
      DELETE /api/documents/{id} → borra (solo admin; scope "write")
      POST /api/documents/{id}/publish → publica (dueño o admin; scope "write")

Al arrancar se siembra el dataset demo (2 empresas, 4 usuarios, 5 docs) en
POSTGRESQL — ver app/storage.py y app/db.py. El seed es IDEMPOTENTE: si la
DB ya tiene datos, no duplica. La corrección automática es:
`bash scripts/verificar_authz.sh`
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import storage
from app.models import Health
from app.controllers import auth_controller, documents_controller, users_controller


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan: siembra el dataset demo al arrancar (solo la primera vez:
    las tablas persisten en PostgreSQL, no se reinician en cada arranque)."""
    storage.seed()
    yield


DESCRIPTION = """
## Autorización RBAC — 2026

API de documentos con **roles** (`admin` · `editor` · `viewer`), **object-level
access control** (cada doc tiene dueño), **scopes** (lo que el TOKEN puede
hacer) y **multi-tenancy** (cada empresa ve SOLO la suya, deny-by-default).

**Usuarios demo** (password `demo12345` para todos):

| Email | Rol | Empresa |
|-------|-----|---------|
| `admin@acme.com` | admin | Acme (1) |
| `editor@acme.com` | editor | Acme (1) |
| `viewer@acme.com` | viewer | Acme (1) |
| `admin@globex.com` | admin | Globex (2) |

**Documentos demo**: `#1` público · `#2` privado (admin acme) · `#3` privado
(editor acme) · `#4` público · `#5` privado (globex).

Probá la matriz de autorización: `bash scripts/verificar_authz.sh`
"""

app = FastAPI(
    title="Módulo 06 — Autorización RBAC",
    description=DESCRIPTION,
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/api/health", response_model=Health, tags=["0 · Health"])
def health():
    """El estado de la demo: cuántos users/docs/tenants hay en PostgreSQL."""
    return Health(
        status="Funciona",
        users_count=storage.user_count(),
        documents_count=storage.document_count(),
        tenants_count=storage.tenant_count(),
        note="Corré scripts/verificar_authz.sh para validar la matriz completa.",
    )


app.include_router(auth_controller.router)
app.include_router(users_controller.router)
app.include_router(documents_controller.router)


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
"""
Persistencia REAL — PostgreSQL vía SQLModel (infraestructura de la cátedra).

Este taller reúne TODOS los temas de la saga:
  - Módulo 02/03: arquitectura en capas + persistencia con SQLModel.
  - Módulo 04/05: autenticación (JWT) y los 7 métodos de identidad.
  - Módulo 06: AUTORIZACIÓN (roles, scopes, tenancy, object-level).

Lo nuevo de ESTE módulo: los usuarios que loguean ("autenticados") y los que
reciben un rol ("autorizados") viven en una base de datos REAL y PERSISTEN
entre reinicios del servidor. El seed es IDEMPOTENTE: siembra el dataset demo
SOLO la primera vez (si las tablas ya tienen datos, no duplica nada).

Las tablas (SQLModel) son el "storage" interno. La capa de negocio escribe
contra las funciones de app/storage.py — los alumnos completan los 4
archivos 🔓 de autorización SIN tocar nada de acá.

Este archivo NO se modifica en la entrega.
"""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel, create_engine

from app.config import DATABASE_URL

# Conector único. En dev el default apunta a localhost:5432 (postgres del
# compose); el backend de docker recibe DATABASE_URL por variable de entorno.
engine = create_engine(DATABASE_URL, echo=False)


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── Tablas ─────────────────────────────────────────────────────────────────


class TenantDB(SQLModel, table=True):
    """Una empresa. El multi-tenancy: cada usuario pertenece a UNA."""

    __tablename__ = "tenants"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)


class UserDB(SQLModel, table=True):
    """El usuario PERSISTIDO: credenciales, rol y tenant.

    - role: "admin" | "editor" | "viewer" (guardamos Role.value como str).
    - tenant_id: FK a tenants — el usuario ve SOLO los datos de su empresa.
    - email: UNIQUE — el login y el seed dependen de que no se duplique.
    """

    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    password_hash: str
    role: str
    tenant_id: int = Field(foreign_key="tenants.id", index=True)
    created_at: datetime = Field(default_factory=_now)


class DocumentDB(SQLModel, table=True):
    """El recurso protegido: dueño (object-level), empresa (tenancy), estado."""

    __tablename__ = "documents"

    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="users.id", index=True)
    tenant_id: int = Field(foreign_key="tenants.id", index=True)
    title: str
    content: str
    visibility: str  # "public" | "private"
    published: bool = False
    created_at: datetime = Field(default_factory=_now)


def create_db_and_tables() -> None:
    """Crea las tablas si no existen (idempotente por definición)."""
    SQLModel.metadata.create_all(engine)
"""
Modelos Pydantic — contratos de entrada/salida de la API del módulo 06.

La novedad respecto del módulo 04/05 es el MODELO DE ROLES:
  - User.role      → "admin" | "editor" | "viewer"   (qué podés hacer)
  - User.tenant_id → la empresa a la que pertenecés (qué datos ves)

Y el modelo Document, que es el RECURSO que se protege:
  - owner_id    → quién lo creó (object-level access control, IDOR)
  - tenant_id   → de qué empresa es (multi-tenancy)
  - visibility  → "public" | "private"  (quién lo ve)
  - published   → draft vs publicado (quién puede publicarlo)

Separación User (almacén interno, incluye el hash) vs UserRead (salida sin
hash): la misma lección del Módulo 04 — el hash NUNCA sale por la API.

Este archivo NO se modifica en la entrega.
"""

import enum
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── Roles ──────────────────────────────────────────────────────────────────


class Role(str, enum.Enum):
    """Los 3 roles del sistema. No hay más: si querés más, es otra entrega."""

    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


# ── Usuario ────────────────────────────────────────────────────────────────


class User(BaseModel):
    """El usuario en el almacén interno (incluye el hash + rol + tenant)."""

    id: int
    email: EmailStr
    name: str
    password_hash: str
    role: Role
    tenant_id: int
    created_at: datetime = Field(default_factory=_now)


class UserCreate(BaseModel):
    """Entrada al registrarse. El nuevo usuario SIEMPRE nace como viewer."""

    email: EmailStr
    name: str = Field(min_length=2, max_length=60)
    password: str = Field(min_length=8, max_length=72)
    tenant_id: int | None = None  # si no se pasa, cae en el tenant por defecto


class UserRead(BaseModel):
    """Salida del usuario — sin password_hash, con rol y tenant."""

    id: int
    email: EmailStr
    name: str
    role: Role
    tenant_id: int
    created_at: datetime


class RoleChange(BaseModel):
    """Body del PATCH /api/users/{id}/role (lo que un admin puede cambiar)."""

    role: Role


# ── Documento (el recurso protegido) ───────────────────────────────────────


class Document(BaseModel):
    """El documento tal como vive en el almacén."""

    id: int
    owner_id: int
    tenant_id: int
    title: str
    content: str
    visibility: Literal["public", "private"]
    published: bool = False
    created_at: datetime = Field(default_factory=_now)


class DocumentCreate(BaseModel):
    """Entrada al crear un documento. Nace como draft privado del autor."""

    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=5000)


class DocumentUpdate(BaseModel):
    """Entrada al editar. Todos los campos son opcionales pero al menos uno."""

    title: str | None = None
    content: str | None = None
    visibility: Literal["public", "private"] | None = None


class DocumentRead(BaseModel):
    """Salida del documento. La visibilidad/published se resuelven al leer."""

    id: int
    owner_id: int
    tenant_id: int
    title: str
    content: str
    visibility: Literal["public", "private"]
    published: bool
    created_at: datetime


# ── Autenticación ──────────────────────────────────────────────────────────


class LoginBody(BaseModel):
    """Body del login. `scope` es OPCIONAL y limita lo que ESTE token puede hacer.

    - scope="read":       token de SOLO lectura (aunque el usuario sea admin).
    - scope="read write": lectura + escritura.
    - scope=None:         el default del rol (viewer→"read", editor/admin→"read write").
    """

    email: EmailStr
    password: str
    scope: Literal["read", "read write"] | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Utilidades ─────────────────────────────────────────────────────────────


class Health(BaseModel):
    status: str
    users_count: int
    documents_count: int
    tenants_count: int
    note: str


class Message(BaseModel):
    message: str
"""
Modelos Pydantic — contratos de entrada/salida de la API.

La separación User (tabla/alma del dato) vs UserRead (salida sin hash) es la
misma lección del Módulo 04: el hash NUNCA sale por la API. Acá no hay tabla
SQL (storage en memoria), pero el principio se mantiene.
"""

from datetime import datetime, timezone

from pydantic import BaseModel, Field, EmailStr


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(BaseModel):
    """El usuario en el almacén interno (incluye el hash)."""

    id: int
    email: EmailStr
    name: str
    password_hash: str
    created_at: datetime = Field(default_factory=_now)

    @property
    def salt(self) -> str:
        # Solo para mostrar en la matriz: el hash lleva la sal adentro.
        return self.password_hash.split("$")[3][:6] if "$" in self.password_hash else ""


class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=60)
    password: str = Field(min_length=8, max_length=72)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    name: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Message(BaseModel):
    message: str


class SSOExplain(BaseModel):
    flow: str
    steps: list[str]


class Health(BaseModel):
    status: str
    users_count: int
    sessions_count: int
    api_tokens_count: int
    login_failures_count: int
    note: str
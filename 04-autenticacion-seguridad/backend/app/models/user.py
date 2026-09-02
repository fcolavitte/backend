"""
Modelo de la entidad User — SQLModel.

Acá definimos al USUARIO: cómo se guarda en la base, qué entra por la API
al registrarse, qué entra al loguearse y qué se devuelve (jamás el hash).

LA LECCIÓN DE SEGURIDAD Nº1 ya está acá, aunque no la veas todavía:
    >>> La contraseña NUNCA se guarda en texto plano. <<<
    En la base no existe la columna `password`: existe `hashed_password`.
    El texto plano se convierte en un hash irreversible ANTES de llegar acá
    (eso lo hacés vos en `security.py`).

Y la LECCIÓN Nº2:
    >>> El hash tampoco se expone en la respuesta. <<<
    Fijate que `UserRead` (lo que devuelve la API) NO tiene `hashed_password`.
"""

from datetime import datetime

from pydantic import EmailStr
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """
    Los campos comunes. El email es la "identidad pública" del usuario:
    con él se loguea y es único en todo el sistema.
    """

    # EmailStr valida que sea un email bien formado (requiere email-validator).
    # `unique=True` crea una constraint en la base: dos users no pueden
    # compartir email.
    email: EmailStr = Field(index=True, unique=True, max_length=255)


class User(UserBase, table=True):
    """
    La TABLA. `table=True` → esta clase es la tabla `users`.

    Campos:
      - id             → primary key
      - hashed_password→ el hash (NO el texto plano) de la contraseña
      - created_at     → timestamp que genera LA BASE (server_default)
    """

    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)

    hashed_password: str

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )


class UserCreate(UserBase):
    """
    Lo que el cliente envía para REGISTRARSE: email + contraseña en texto
    plano. Es texto plano SOLO en este punto (el request). Después de acá,
    se hashea y el texto plano se descarta.
    """

    password: str = Field(min_length=8, max_length=128)


class UserLogin(SQLModel):
    """
    Lo que el cliente envía para LOGUEARSE: email + contraseña.
    (Se separa de UserCreate porque son operaciones distintas: registrar
    crea un recurso; loguear verifica credenciales.)
    """

    email: EmailStr
    password: str


class UserRead(UserBase):
    """
    Lo que la API devuelve: el usuario SIN el hash.

    Pregunta de la clase: ¿por qué `UserRead` NO hereda de `User` (la
    tabla) sino de `UserBase`? Porque `User` tiene `hashed_password`, y
    eso jamás debe salir por la API.
    """

    id: int
    created_at: datetime


class Token(SQLModel):
    """
    Lo que devuelve el login: el JWT y su tipo.
    El `access_token` es el string firmado que el cliente reenvía en cada
    request (header `Authorization: Bearer <token>`).
    """

    access_token: str
    token_type: str = "bearer"

"""
Capa de infraestructura — la conexión a la base de datos.

Idéntico al Módulo 03: acá vive TODO lo que toca PostgreSQL (la URL, el
engine y la creación de tablas). Ninguna otra capa importa al driver
directamente: solo piden una `Session`.

En este módulo la única novedad es que, además de la tabla `tasks`, va a
existir la tabla `users` (definida en `models/user.py` con `table=True`).
"""

import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/postgres",
)

# El ENGINE se crea UNA sola vez. Sabe hablar con PostgreSQL.
engine = create_engine(DATABASE_URL)


def create_db_and_tables() -> None:
    """
    Crea las tablas a partir de los modelos ORM (`table=True`).

    Idempotente: si la tabla ya existe, no la toca. Al importar todos los
    modelos (vía los controllers que registra `main.py`), SQLModel los
    conoce y puede generar el `CREATE TABLE` de `users` y de `tasks`.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Proporciona una SESIÓN por cada request (generador para FastAPI).

    Se abre al empezar el request y se cierra al terminar (el `with`
    hace commit/rollback automático según haya error o no).
    """
    with Session(engine) as session:
        yield session

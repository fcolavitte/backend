"""
Capa de datos (Repository) — acceso a la entidad User.

COMPLETÁ los métodos marcados con TODO. Usá el ORM (SQLModel), igual que
en el Módulo 03. Pensás en objetos (`User`), no en filas y columnas.

Pistas rápidas (el GUIA_ALUMNO tiene las consignas completas):
  - buscar por email → select(User).where(User.email == email) + .first()
  - leer por id      → session.get(User, user_id)
  - crear            → User(...) + session.add() + commit() + refresh()

Recordá la lección del Módulo 03: el repository NO sabe de HTTP ni de
reglas de negocio. Solo habla con la base. Devolvés `None` si no encontrás;
el que decide qué significa eso (401, 409, 404) es la capa de arriba.
"""

from sqlmodel import Session, select

from app.models.user import User


class UserRepository:
    """Acceso a datos de la entidad User."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> User | None:
        """
        Devuelve el usuario con ese email, o None si no existe.

        Pista: `select(User).where(User.email == email)`, ejecutás con
        `self.session.exec(...)` y usás `.first()` (no `.all()`) porque
        querés UNO o None.
        """
        raise NotImplementedError("TODO: implementar get_by_email")

    def get_by_id(self, user_id: int) -> User | None:
        """
        Devuelve el usuario por id, o None si no existe.

        Pista: el ORM tiene atajo — `self.session.get(User, user_id)`.
        """
        raise NotImplementedError("TODO: implementar get_by_id")

    def create(self, email: str, hashed_password: str) -> User:
        """
        Crea un usuario y devuelve la instancia persistida (con id y fecha).

        Pista: `User(email=email, hashed_password=hashed_password)`, luego
        `add()`, `commit()` y `refresh()` para traer id + created_at.
        """
        raise NotImplementedError("TODO: implementar create")

    def count(self) -> int:
        # EJEMPLO resuelto — te sirve de referencia (el health lo usa).
        statement = select(User)
        return len(self.session.exec(statement).all())

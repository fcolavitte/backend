"""
Almacenamiento EN MEMORIA (para el ejemplo).

En producción esto es una base de datos (PostgreSQL, etc.). Acá usamos dicts
en memoria para que el módulo sea autocontenido: corre sin infra.

ESTRUCTURA de lo que se guarda, que es LA LECCIÓN:
  - users:        id → User               (existe en TODOS los métodos)
  - sessions:     token → SessionData     (SOLO Session Based: estado en server)
  - api_tokens:   token → TokenData       (SOLO Token Auth opaco: estado en server)
  - JWT / Basic   → NO guardan nada acá    (stateless: el "estado" vive en el token)

Mirá /api/health mientras hacés login con cada método: los contadores te
muestran CUÁL guarda estado y cuál no. Eso es la lección viva.
"""

from datetime import datetime, timedelta, timezone
from threading import RLock

from app import security
from app.config import DEMO_EMAIL, DEMO_PASSWORD, SESSION_EXPIRE_MINUTES, TOKEN_EXPIRE_MINUTES
from app.models import User, UserCreate

# RLock (reentrante): seed_demo_user adquiere el lock y llama a create_user,
# que también lo adquiere. Con Lock() normal eso es un DEADLOCK.
_lock = RLock()


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── Estado en memoria ──────────────────────────────────────────────────────

users: dict[int, User] = {}
sessions: dict[str, dict] = {}    # token opaco → {"user_id", "expires_at"}
api_tokens: dict[str, dict] = {}  # token opaco → {"user_id", "expires_at"}

_next_id: int = 1


# ── Usuarios ───────────────────────────────────────────────────────────────


def seed_demo_user() -> None:
    """Crea el usuario demo (si no existe). Se llama al arrancar."""
    with _lock:
        if any(u.email == DEMO_EMAIL for u in users.values()):
            return
        body = UserCreate(
            email=DEMO_EMAIL,
            name="Usuario Demo",
            password=DEMO_PASSWORD,
        )
        create_user(body)


def create_user(body: UserCreate) -> User:
    global _next_id
    with _lock:
        user = User(
            id=_next_id,
            email=body.email,
            name=body.name,
            password_hash=security.hash_password(body.password),
        )
        users[user.id] = user
        _next_id += 1
        return user


def get_user_by_email(email: str) -> User | None:
    with _lock:
        for u in users.values():
            if u.email == email.lower().strip():
                return u
    return None


def get_user_by_id(user_id: int) -> User | None:
    with _lock:
        return users.get(user_id)


def user_exists(email: str) -> bool:
    return get_user_by_email(email) is not None


def user_count() -> int:
    with _lock:
        return len(users)


# ── Sesiones server-side (SESSION BASED) ───────────────────────────────────


def create_session(user_id: int) -> str:
    """Crea una sesión: genera un token opaco y LO GUARDA (estado en server)."""
    token = security.new_opaque_token()
    with _lock:
        sessions[token] = {
            "user_id": user_id,
            "expires_at": _now() + timedelta(minutes=SESSION_EXPIRE_MINUTES),
        }
    return token


def get_session(token: str) -> dict | None:
    """Busca la sesión. Si expiró, la borra y devuelve None (revocación implícita)."""
    with _lock:
        data = sessions.get(token)
        if data is None:
            return None
        if data["expires_at"] < _now():
            del sessions[token]
            return None
        return data


def delete_session(token: str) -> None:
    """Borra la sesión → REVOCACIÓN INMEDIATA (la ventaja de server-side)."""
    with _lock:
        sessions.pop(token, None)


def session_count() -> int:
    with _lock:
        return len(sessions)


# ── Tokens opacos (TOKEN AUTH) ─────────────────────────────────────────────


def create_api_token(user_id: int) -> str:
    """Crea un token opaco y LO GUARDA (también estado en server)."""
    token = security.new_opaque_token()
    with _lock:
        api_tokens[token] = {
            "user_id": user_id,
            "expires_at": _now() + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
        }
    return token


def get_api_token(token: str) -> dict | None:
    with _lock:
        data = api_tokens.get(token)
        if data is None:
            return None
        if data["expires_at"] < _now():
            del api_tokens[token]
            return None
        return data


def delete_api_token(token: str) -> None:
    with _lock:
        api_tokens.pop(token, None)


def api_token_count() -> int:
    with _lock:
        return len(api_tokens)
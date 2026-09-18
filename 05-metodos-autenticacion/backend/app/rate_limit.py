"""
Rate limiting del login (anti brute-force / credential stuffing).

Problema que resuelve: un atacante puede probar millones de contraseñas
contra /api/auth/*/login. Cada intento cuesta Argon2 (deliberadamente LENTO),
así que esto también protege el CPU del server contra abuso.

Solución acá (didáctica, en memoria):

  - Contamos INTENTOS FALLIDOS por email dentro de una ventana de tiempo.
  - Si pasás el máximo (5), el email queda bloqueado 15 minutos → 429.
  - El login EXITOSO resetea el contador (el usuario legítimo no acumula).
  - Es lo mismo que hace un lockout clásico, sin password ni bloqueo 'duro'.

POR QUÉ en memoria y no en Redis (producción REAL):
  - Este ejemplo es monoproceso y autocontenido → un dict alcanza.
  - En producción con MÚLTIPLES instancias, cada una tendría SU contador:
    un atacante podría rotar de instancia y esquivar el límite. Ahí el estado
    tiene que vivir en un almacén compartido (Redis) o en un gateway
    (nginx/Cloudflare WAF). La LÓGICA es la misma; cambia el storage.

  - Nota de seguridad: el bloqueo es por EMAIL. Un atacante que prueba contra
    MUCHOS emails distintos desde UNA IP no se frena acá: eso es el rate limit
    por IP, que en producción se hace en el gateway (capa de red, antes de
    llegar al app server).
"""

from datetime import datetime, timedelta, timezone
from threading import RLock

from app.config import LOGIN_MAX_FAILED_ATTEMPTS, LOGIN_RATE_WINDOW_MINUTES

_lock = RLock()

# email → [timestamps de intentos fallidos dentro de la ventana]
_failures: dict[str, list[datetime]] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _prune(key: str) -> None:
    """Descarta intentos viejos (fuera de la ventana)."""
    cutoff = _now() - timedelta(minutes=LOGIN_RATE_WINDOW_MINUTES)
    _failures[key] = [ts for ts in _failures[key] if ts > cutoff]
    if not _failures[key]:
        del _failures[key]


def register_failure(email: str) -> None:
    """Anota un intento fallido para este email."""
    key = email.lower().strip()
    with _lock:
        _failures.setdefault(key, []).append(_now())


def clear_failures(email: str) -> None:
    """Reset del contador — se llama en login EXITOSO."""
    key = email.lower().strip()
    with _lock:
        _failures.pop(key, None)


def is_blocked(email: str) -> bool:
    """¿Este email superó el máximo de fallos en la ventana?"""
    key = email.lower().strip()
    with _lock:
        if key not in _failures:
            return False
        _prune(key)
        return len(_failures.get(key, [])) >= LOGIN_MAX_FAILED_ATTEMPTS


def failure_count() -> int:
    """Total de intentos fallidos vivos en la ventana (para /api/health)."""
    with _lock:
        total = 0
        for key in list(_failures):
            _prune(key)
            total += len(_failures.get(key, []))
        return total
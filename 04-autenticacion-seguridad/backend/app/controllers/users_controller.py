"""
Capa de presentación (Controller) — endpoints del usuario autenticado.

COMPLETÁ el endpoint marcado con TODO. Acá viven las rutas que SOLO
puede usar alguien autenticado. La magia está en `Depends(get_current_user)`:
FastAPI ejecuta esa dependencia ANTES del endpoint; si falla (token inválido,
expirado, o usuario inexistente), devuelve 401 y el endpoint ni corre.
"""

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models.user import User, UserRead

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    """
    GET /api/users/me — devuelve el usuario autenticado.

    Fijate: NO recibe un id por la URL. El "quién" viene del TOKEN, resuelto
    por `get_current_user`. Acá solo devolvés `current_user`.

    🧠 Esta es la diferencia con el Módulo 03: antes cualquiera podía
    `GET /api/tasks/{id}` y leer lo que quisiera. Ahora el server sabe quién
    sos, y vos decidís qué devolverle.
    """
    raise NotImplementedError("TODO: implementar read_me")

"""
Health check — capa de presentación (DADO, es tu ejemplo vivo).

Mirá cómo recibe el service con `Depends(get_auth_service)`. Ese es el
patrón que vas a repetir en el `auth_controller` y en `users_controller`.
"""

from fastapi import APIRouter, Depends

from app.dependencies import get_auth_service
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health_check(service: AuthService = Depends(get_auth_service)):
    """GET /api/health — verifica que el servicio y la base responden."""
    return {
        "status": "Funciona",
        "service": "04-autenticacion-seguridad-backend",
        "db": "conectada",
        "users_count": service.count_users(),
    }

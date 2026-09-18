"""Controller de autenticación — register + login.

NO se modifica: la autenticación ya fue evaluada en los módulos 04/05.
Acá solo se ajustó el login para emitir el JWT con los claims de
autorización (role, tenant_id, scope).

La regla del scope (lección del Pilar 3):
  - Si el login NO pide scope → el token recibe el default del rol
    (viewer → "read", editor/admin → "read write").
  - Si el login pide un scope, ese scope NO puede EXCEDER el default del
    rol: un viewer no puede pedir "read write" (sería auto-elevarse).
    Si lo pide → 400.
  - El scope termina en el TOKEN. La autorización lo lee de ahí.
"""

from fastapi import APIRouter, HTTPException, status

from app import auth_common, security, storage
from app.models import (
    LoginBody,
    Role,
    Token,
    UserCreate,
    UserRead,
)

router = APIRouter(prefix="/api")

# Escopos por rol: un rol habilita al MUCHO estos scopes.
ROLE_DEFAULT_SCOPES: dict[str, str] = {
    Role.VIEWER.value: "read",
    Role.EDITOR.value: "read write",
    Role.ADMIN.value: "read write",
}


def _resolve_scope(user_role: Role, requested: str | None) -> str:
    """El scope final del token. Nunca puede superar el del rol."""
    default = ROLE_DEFAULT_SCOPES[user_role.value]
    if requested is None:
        return default
    if requested not in ("read", "read write"):
        raise HTTPException(status_code=400, detail="Scope inválido. Usá 'read' o 'read write'.")
    requested_parts = set(requested.split())
    default_parts = set(default.split())
    if not requested_parts.issubset(default_parts):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tu rol ({user_role.value}) no permite el scope '{requested}'.",
        )
    return requested


@router.post("/auth/register", response_model=UserRead, status_code=201, tags=["1 · Auth"])
def register(body: UserCreate):
    """Registra un usuario. SIEMPRE nace como viewer de un tenant.

    El rol lo asigna un admin después (PATCH /api/users/{id}/role). Si no se
    pasa tenant_id, cae en Acme (tenant 1).
    """
    user = storage.create_user(body)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado",
        )
    return user


@router.post("/auth/login", response_model=Token, tags=["1 · Auth"])
def login(body: LoginBody):
    """Login → JWT con claims de autorización: role, tenant_id y scope."""
    user = auth_common.verify_login(body.email, body.password)

    scope = _resolve_scope(user.role, body.scope)
    access_token = security.create_access_token(
        subject=str(user.id),
        extra_claims={
            "role": user.role.value,
            "tenant_id": user.tenant_id,
            "scope": scope,
        },
    )
    return Token(access_token=access_token, token_type="bearer")
"""Mini-app FastAPI que USA las funciones puras.

Ojo: los tests unitarios de este módulo NO levantan esta app. Testean
`rules.py` y `password.py` directamente (funciones puras). Levantar la app
y pegarle a los endpoints es un test de INTEGRACIÓN, tema del próximo módulo.

Esta app está acá solo para mostrar el patrón: el código de producción
(las funciones puras) vive separado y es reutilizable/testeable, y el
framework (FastAPI) es una cáscara fina que las invoca.
"""

from fastapi import FastAPI

from app import password, rules

app = FastAPI(title="07 — Testing unitario")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/authz/can-edit")
def can_edit(owner_id: int, user_id: int, role: str) -> dict:
    """Expone la regla pura can_edit como endpoint (ejemplo)."""
    return {"allowed": rules.can_edit(owner_id, user_id, role)}


@app.get("/auth/password-errors")
def password_errors(p: str) -> dict:
    """Expone la regla pura validate_password como endpoint (ejemplo)."""
    return {"errors": password.validate_password(p)}

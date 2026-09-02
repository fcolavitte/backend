"""
Módulo 04 — Autenticación y Seguridad
=====================================

Sobre la base del Módulo 03 (capas + ORM) agregamos la CAPA DE SEGURIDAD:

    - Registro de usuarios (register) → hash de contraseña con Argon2
    - Login → verificación + emisión de un token JWT
    - Endpoint protegido → `/api/users/me` solo accesible con token válido

La arquitectura se mantiene: Controller → Service → Repository → DB.
Lo nuevo es un módulo `security.py` (hash + JWT) y una dependencia
`get_current_user` que protege rutas.

Este archivo es SOLO el entrypoint: crea la app, registra los routers y
maneja el arranque. No tiene lógica de negocio, ni SQL, ni seguridad.

Antes de ejecutar:
    1. Copiá `.env.example` a `.env` y completá DATABASE_URL + SECRET_KEY
    2. `uv sync` para instalar dependencias (incluye pwdlib[argon2] y pyjwt)

Ejecutar:
    uv run -m app.main
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers import auth_controller, health_controller, users_controller
from app.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Al arrancar: crea las tablas (si no existen).
    Al apagar: nada que liberar (la Session se cierra sola por request).
    """
    create_db_and_tables()
    yield


app = FastAPI(
    title="Autenticación y Seguridad — API de Usuarios",
    description=(
        "Módulo 04 — Registro, login, sesiones (JWT vs server-side) y "
        "seguridad OWASP. Sobre la arquitectura en capas del Módulo 03."
    ),
    version="0.4.0",
    lifespan=lifespan,
)

# CORS: mismo config que los módulos anteriores. En producción, dominios específicos.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: listar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registramos los routers. Cada controller expone sus propios endpoints.
app.include_router(health_controller.router)
app.include_router(auth_controller.router)
app.include_router(users_controller.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

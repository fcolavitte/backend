"""
Entrypoint del módulo 05 — Comparativa de métodos de autenticación.

Levanta la API con los 7 métodos andando lado a lado:

  1 · Basic Auth        GET  /api/me/basic
  2 · Session Based     POST /api/auth/session/login   → cookie session_id
                       GET  /api/me/session
  3 · Token Auth        POST /api/auth/token/login      → token opaco en header
                       GET  /api/me/token
  4 · JWT (header)      POST /api/auth/jwt/login        → JWT en header
                       GET  /api/me/jwt
  5 · Cookie Based      POST /api/auth/jwt-cookie/login → JWT en cookie
                       GET  /api/me/jwt-cookie
  6 · OAuth2 (pwd flow) POST /api/auth/oauth2/token     → JWT (form, estándar)
                       GET  /api/me/oauth2
  7 · SSO (simulado)    GET  /api/sso/explain
                       POST /api/sso/simulate           → id_token de "IdP"
                       GET  /api/me/sso

El /api/health es LA LECCIÓN VIVA: muestra cuántas sesiones y tokens opacos
hay guardados en el server. Logueate con Session/Token Auth y el contador
sube. Logueate con JWT y no cambia NADA (stateless). Verlo con tus ojos es
entender la diferencia entre stateful y stateless.

Hardening incluido (Nivel 02):
  - Rate limiting de login (5 fallos/15 min → 429) en auth_common.verify_login
  - Security headers globales (app.middleware.SecurityHeadersMiddleware)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import rate_limit, storage
from app.middleware import SecurityHeadersMiddleware
from app.models import Health
from app.methods import (
    basic,
    jwt_cookie,
    jwt_header,
    oauth2,
    session_cookie,
    sso_simulado,
    token_bearer,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan: lo que corre al arrancar y al apagar el server.

    (on_event está deprecado en FastAPI — la práctica 2026 es lifespan.)
    """
    storage.seed_demo_user()
    yield

DESCRIPTION = """
## Comparativa de métodos de autenticación — 2026

Siete formas de autenticar una API FastAPI, andando lado a lado.
Cada método tiene su propio botón **Authorize** en Swagger.

| # | Método | ¿Dónde vive el estado? | ¿Viaja por dónde? |
|---|--------|------------------------|-------------------|
| 1 | Basic Auth | en cada request (nada) | header `Authorization: Basic` |
| 2 | Session Based | **en el server** (sesiones) | cookie httpOnly |
| 3 | Token Auth (opaco) | **en el server** (api_tokens) | header `Authorization: Bearer` |
| 4 | JWT header | en el token (firmado) | header `Authorization: Bearer` |
| 5 | JWT cookie | en el token (firmado) | cookie httpOnly |
| 6 | OAuth2 + JWT | en el token (firmado) | header `Authorization: Bearer` |
| 7 | SSO (OIDC sim.) | en el token del IdP (validado) | header `Authorization: Bearer` |

**Usuario demo**: `demo@ejemplo.com` / `demo12345`

Mirá **/api/health** después de cada login: los contadores te muestran
qué métodos guardan estado (2 y 3) y cuáles no (1, 4, 5, 6, 7).

#### Hardening incluido (Nivel 02)

- **Rate limiting** en los 5 endpoints de login: 5 intentos fallidos por
  email en 15 min → `429 Too Many Requests` (+ `Retry-After`).
- **Security headers** en todas las respuestas (HSTS, nosniff, X-Frame-Options,
  Referrer-Policy) y `Cache-Control: no-store` en `/api/me/*`.
- **SECRET_KEY fail-loud**: en producción (`ENVIRONMENT=production`) la app
  NO arranca sin `SECRET_KEY` en el entorno. Sin defaults silenciosos.
- **COOKIE_SECURE config-driven**: `COOKIE_SECURE=true` en producción (HTTPS).

Consultá `docs/OWASP.md` para el mapeo honesto OWASP Top 10 → qué cubre el
módulo, qué no, y cómo se hace en un proyecto real.
"""

app = FastAPI(
    title="Módulo 05 — Métodos de Autenticación",
    description=DESCRIPTION,
    version="0.1.0",
    lifespan=lifespan,
)

# Hardening de capa HTTP: security headers en TODAS las respuestas.
app.add_middleware(SecurityHeadersMiddleware)


@app.get("/api/health", response_model=Health, tags=["0 · Health"])
def health():
    """El contador vivo: mirá cómo cambia con cada método.

    - users_count:          crece al registrarte / entrar por SSO (JIT).
    - sessions_count:       SOLO crece con Session Based (estado en server).
    - api_tokens_count:     SOLO crece con Token Auth opaco (estado en server).
    - login_failures_count: intentos fallidos vivos en la ventana del rate
                            limiter (probalo: 5 logins mal = 429 + counter 5).
    """
    return Health(
        status="Funciona",
        users_count=storage.user_count(),
        sessions_count=storage.session_count(),
        api_tokens_count=storage.api_token_count(),
        login_failures_count=rate_limit.failure_count(),
        note="Logueate con cada método y mirá qué contadores cambian.",
    )


# ── Routers de los 7 métodos ───────────────────────────────────────────────

app.include_router(basic.router)
app.include_router(session_cookie.router)
app.include_router(token_bearer.router)
app.include_router(jwt_header.router)
app.include_router(jwt_cookie.router)
app.include_router(oauth2.router)
app.include_router(sso_simulado.router)


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
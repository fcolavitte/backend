# Módulo 05 — Métodos de Autenticación

> **Clase asincrónica** — debido a paro nacional 08/sept/2026 · Desarrollo de Software 2026 (UTN)
>
> Material autocontenido: no dependés del Módulo 04 para hacerlo. Backend de
> ejemplo en FastAPI con los **7 métodos de autenticación funcionando lado a lado**.

## ¿De qué va este módulo?

Distinto a lo que se suele creer, **no hay "un" mejor método**. Hay *categorías
ortogonales* que se combinan. Ese es el gran aprendizaje del módulo.

> Los 7 "métodos" no son 7 competidores. Son **dimensiones distintas** que se
> pueden mezclar. La decisión de diseño es elegir *qué combinás según tu
> contexto de seguridad*, no *cuál gana*.

### Las 7 categorías

| # | Método | Dónde vive el estado | Mecanismo clave |
|---|--------|---------------------|-----------------|
| 1 | **Basic Auth** | Ninguno (credenciales van en cada request) | Header `Authorization: Basic base64(user:pass)` |
| 2 | **Session Based** | Del lado del server | Cookie `session_id` apunta a una sesión guardada |
| 3 | **Token Auth** | Del lado del server (token opaco) | Header `Bearer <token>` que es una referencia |
| 4 | **JWT** | Stateless (todo va dentro del token) | Token firmado, auto-contenido |
| 5 | **Cookie Based (JWT)** | En la cookie (firma) | JWT en cookie `httpOnly` |
| 6 | **OAuth2** | Delegación de autorización | Protocolo: el client obtiene un token del resource server |
| 7 | **SSO** | IdP externo | OIDC: un solo login, muchas apps |

## Qué vas a aprender

- **El mapa mental** para no confundir método con transporte ni con protocolo.
- Por qué **JWT y Session no compiten**: uno es stateless, el otro stateful.
- **Basic vs Control vs Token vs JWT** como niveles de seguridad crecientes.
- La diferencia entre **quién autentica** (Basic, Session, SSO) y **cómo se
  transporta la credencial** (header, cookie).
- OAuth2 y SSO como **delegación**: la app que pide el login NO guarda la password.
- **La honestidad de seguridad**: qué cubre este módulo y qué NO
  (→ [docs/OWASP.md](docs/OWASP.md)): autenticación (A07) ≠ autorización (A01).
- **Buenas prácticas 2026**: Argon2id (no más bcrypt ni `#hashlib`), JWT con
  `algorithms` explícito y `iss`/`aud` validados, cookies `httpOnly` + `Secure`,
  rate limiting del login, security headers.

## Estructura del repositorio

```
05-metodos-autenticacion/
├── backend/                  # Proyecto FastAPI (autocontenido, sin base de datos)
│   ├── pyproject.toml        # Dependencias (pwdlib[argon2], pyjwt, ...)
│   └── app/
│       ├── config.py         # Configuración (SECRET_KEY fail-loud, COOKIE_SECURE)
│       ├── security.py       # Argon2id + firma/validación de JWT
│       ├── models.py         # Modelos Pydantic (User, Token, LoginForm, Health...)
│       ├── storage.py        # Almacenamiento en memoria (dicts + RLock)
│       ├── auth_common.py    # verify_login: rate limit + timing attack + 401/429
│       ├── rate_limit.py     # Anti brute-force: 5 fallos por email → 429 (Nivel 02)
│       ├── middleware.py     # Security headers globales (HSTS, nosniff, ...) (Nivel 02)
│       ├── main.py           # FastAPI app con /api/health y los 7 routers
│       └── methods/          # Un archivo por método
│           ├── basic.py
│           ├── session_cookie.py
│           ├── token_bearer.py
│           ├── jwt_header.py
│           ├── jwt_cookie.py
│           ├── oauth2.py
│           └── sso_simulado.py
├── frontend/                 # Laboratorio web: probá los 7 métodos con clicks
│   ├── src/
│   │   ├── api.ts            # UN mecanismo por método, documentado
│   │   ├── App.tsx           # tabs + HealthBar + consola de requests
│   │   └── components/panels/  # un panel por método + rate limit
│   ├── pnpm-workspace.yaml   # pnpm (npm está bloqueado en la facultad)
│   └── README.md             # cómo arrancarlo y qué probar
├── postman/
│   └── 05-metodos-autenticacion.postman_collection.json
├── scripts/
│   └── verificar_metodos.sh  # Valida los 7 métodos + rate limit + headers (25 checkpoints)
└── docs/
    ├── MATERIAL_AULA.md      # Plan de la clase (leé → mirá → hacé)
    ├── MATRIZ_COMPARATIVA.md # Los 7 métodos × dimensiones
    ├── CASOS_DE_USO.md       # Diseño guiado por seguridad (cuándo usar cuál)
    ├── OWASP.md              # ⭐ Mapeo honesto OWASP Top 10 → qué cubre y qué NO
    ├── NIVEL_03_AUTORIZACION.md  # ⭐ Propuesta de la próxima clase: RBAC, scopes, tenancy
    └── GUIAS/
        ├── GUIA_VIDEO_A.md   # Hussein Nasser: autenticaciones de menos a más seguras
        └── GUIA_VIDEO_B.md   # BekBrace: consentimiento OAuth (con nota de librerías)
```

## Cómo levantar y probar (guía rápida)

> Todo el proyecto se levanta con **dos procesos**: el backend (FastAPI, con
> `uv`) y —si querés clicear en vez de escribir requests— el frontend
> laboratorio (Vite, con `pnpm`).

### Requisitos

| Herramienta | Para qué | Cómo verificar |
|-------------|----------|----------------|
| **uv** (≥ 0.5) | backend, `pyproject.toml` + `uv.lock` | `uv --version` |
| **pnpm** (≥ 9) | frontend, `pnpm-lock.yaml` | `pnpm --version` |
| Python ≥ 3.12 | backend | `uv run python --version` |
| Node ≥ 20 | frontend | `node --version` |

> ⚠️ **pnpm, no npm**: el CLI de npm está bloqueado en la facultad. Todo el
> front del curso usa pnpm. Nunca generes `package-lock.json` (npm) acá.

### Paso 1 — Levantar el backend

```bash
cd backend
uv sync                 # instala/crea el .venv según uv.lock
uv run -m app.main      # arranca uvicorn en http://127.0.0.1:8000
```

El usuario demo viene **precargado en memoria** (no hay base de datos):

- **email**: `demo@ejemplo.com`
- **password**: `demo12345`

Sanity check en otra terminal:

```bash
curl http://127.0.0.1:8000/api/health
# → {"status":"Funciona","users_count":2,...}
```

### Paso 2 — Probar (4 vías, eligí una)

| Vía | Cuándo usarla | Cómo |
|-----|---------------|------|
| **1 · Swagger `/docs`** | lo más rápido, zero setup | abrí `http://127.0.0.1:8000/docs` — cada método tiene su botón *Authorize* |
| **2 · Frontend laboratorio** | ver la lección (cookies, JWT, 429) | `cd frontend && pnpm install && pnpm dev` → `http://localhost:5173` |
| **3 · Script de verificación** | correr los 25 checks automáticos | `bash scripts/verificar_metodos.sh` (con el backend arriba) |
| **4 · Postman** | guardar las requests como colección | importá `postman/05-metodos-autenticacion.postman_collection.json` y corré el Collection Runner |

### Paso 3 — Verificación automática (opcional pero recomendado)

```bash
# Con el backend levantado en :8000:
bash scripts/verificar_metodos.sh
# → 25 checkpoints OK (7 métodos + rate limiting + security headers)
```

Si algún check falla, el script te dice cuál y qué HTTP code esperaba.

> **Al apagar**: Ctrl+C en cada proceso. Si querés limpiar el estado en
> memoria (sesiones, tokens, fallos de login), reiniciá el backend: todo
> vuelve a cero.

---

## Detalle del backend

### Variables de entorno (modo producción — Nivel 02)

| Variable | Default (dev) | Producción |
|----------|---------------|------------|
| `ENVIRONMENT` | `development` | `production` |
| `SECRET_KEY` | default dev (NO usar) | **obligatoria** — sin ella la app NO arranca (fail-loud) |
| `COOKIE_SECURE` | `false` (http local) | `true` (HTTPS) |
| `LOGIN_MAX_FAILED_ATTEMPTS` | `5` | ajustable |
| `LOGIN_RATE_WINDOW_MINUTES` | `15` | ajustable |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | ajustable |

```bash
# Producción
ENVIRONMENT=production SECRET_KEY=$(openssl rand -hex 32) COOKIE_SECURE=true uvicorn app.main:app
```

### Endpoints por método

| Método | Endpoint de autenticación | Endpoint protegido |
|--------|---------------------------|--------------------|
| Basic | *(las credenciales van en cada request)* | `GET /api/me/basic` |
| Session Based | `POST /api/auth/session/login` (`json`) | `GET /api/me/session` |
| Session logout | `POST /api/auth/session/logout` | — |
| Token Auth | `POST /api/auth/token/login` (`urlencoded`) | `GET /api/me/token` |
| Token logout | `POST /api/auth/token/logout` | — |
| JWT header | `POST /api/auth/jwt/login` (`json`) | `GET /api/me/jwt` |
| JWT cookie | `POST /api/auth/jwt-cookie/login` (`json`) | `GET /api/me/jwt-cookie` |
| JWT cookie logout | `POST /api/auth/jwt-cookie/logout` | — |
| OAuth2 | `POST /api/auth/oauth2/token` (`form OAuth2`) | `GET /api/me/oauth2` |
| SSO | `POST /api/sso/simulate` | `GET /api/me/sso` |

**Tip**: `GET /api/health` muestra contadores vivos de la memoria (`sessions_count`,
`api_tokens_count`, `users_count`). Logueate con cada método y mirá **qué contador
cambia**. Ahí vas a ver en carne y hueso qué guarda estado y qué no.

## Frontend — Laboratorio interactivo (detalle)

Además de Swagger (`/docs`), Postman y el script, hay un frontend web para
probar los 7 métodos **con clicks**: `frontend/`. Muestra lo que no se ve por
curl:

```bash
# 1) backend corriendo (uvicorn en :8000) y luego:
cd frontend
pnpm install
pnpm dev        # → http://localhost:5173 (proxy a :8000, sin CORS)
```

⚠️ **pnpm, no npm**: el CLI de npm está bloqueado en la facultad. Todo el
front del curso usa pnpm.

## Material de clase

- [Material / plan de clase](docs/MATERIAL_AULA.md) — la ruta leé → mirá → hacé.
- [Matriz comparativa](docs/MATRIZ_COMPARATIVA.md) — 7 métodos × dimensiones.
- [Casos de uso](docs/CASOS_DE_USO.md) — diseño guiado por seguridad.
- [**OWASP Top 10 — mapeo honesto**](docs/OWASP.md) — qué cubre el módulo, qué
  NO, y cómo se hace en un proyecto real (defensa en profundidad).
- [**Nivel 03 — Autorización**](docs/NIVEL_03_AUTORIZACION.md) — la propuesta de
  la próxima clase: RBAC, scopes, tenancy, deny-by-default.
- [Guía Video A](docs/GUIAS/GUIA_VIDEO_A.md) — Hussein Nasser, autenticaciones de menos a más seguras.
- [Guía Video B](docs/GUIAS/GUIA_VIDEO_B.md) — BekBrace, consentimiento OAuth (*con nota sobre librerías obsoletas*).

## Buenas prácticas destacadas (2026)

Estas decisiones están adentro del código de ejemplo, no solo explicadas:

1. **Contraseñas con Argon2id** (`pwdlib`), no bcrypt ni `hashlib` plano.
2. **`DUMMY_HASH` anti timing-attack**: cuando el usuario no existe, igual
   corremos un hash inútil para que el tiempo de respuesta sea indistinguible.
3. **JWT con `algorithms=[ALGORITHM]` explícito** (nunca `algorithms="auto"`),
   y validación de `iss` (issuer) y `aud` (audience) en el SSO.
4. **Cookies `httpOnly` + `secure`** (config-driven con `COOKIE_SECURE`) para
   los métodos basados en cookie: el JS no puede leer el token.
5. **Rate limiting del login (Nivel 02)**: 5 intentos fallidos por email en 15
   minutos → `429 Too Many Requests` con `Retry-After`.
6. **Security headers globales (Nivel 02)**: HSTS, `nosniff`, X-Frame-Options,
   Referrer-Policy, y `Cache-Control: no-store` en las rutas `/api/me/*`.
7. **`SECRET_KEY` fail-loud (Nivel 02)**: en `ENVIRONMENT=production` la app se
   NEGA a arrancar sin `SECRET_KEY` en el entorno. Sin defaults silenciosos.
8. **Revocación inmediata** con sesiones y tokens opacos (viven en el server);
   el JWT no se puede revocar antes de que expire (tradeoff intencional).
9. **SSO con validación estricta**: un JWT local de la misma app es rechazado por
   `/me/sso` porque no tiene el `iss`/`aud` del IdP (lo vemos con la batería de tests).

> ⚠️ **Honestidad primero**: este módulo enseña autenticación (OWASP A07), no
> autorización (A01). Ver [docs/OWASP.md](docs/OWASP.md) para el mapeo completo
> y el camino a un proyecto de producción real.

## Siguiente clase (Nivel 03)

**Autorización — RBAC, scopes y tenancy.** Cierra la brecha #1 del OWASP Top 10
(A01 Broken Access Control): roles y permisos, scopes OAuth reales, deny-by-
default, multi-tenancy, e integración con un IdP real. Ese es el proyecto
práctico que vamos a construir juntos.

→ **[docs/NIVEL_03_AUTORIZACION.md](docs/NIVEL_03_AUTORIZACION.md)** — propuesta
completa de la clase: pilares, matriz de autorización, checklist de entregables
y plan de integración con Keycloak.
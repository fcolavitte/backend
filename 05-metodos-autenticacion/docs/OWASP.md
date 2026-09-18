# OWASP Top 10 — Mapeo honesto del Módulo 05

> Este documento responde una pregunta que TODO dev debería hacerse: **"¿mi
> código está 'a prueba de OWASP Top 10'?"** La respuesta honesta casi siempre
> es **NO**, porque el Top 10 es una lista de *categorías amplísimas* — no
> se "aprueba" en un módulo, se ataca capa por capa en un proyecto real.
>
> Acá te mostramos **qué cubre este módulo, qué NO, y qué harías en un
> proyecto de producción real** para cerrar cada brecha. Es el documento más
> importante del módulo: te da el mapa para no confundir "aprendí 7 métodos
> de auth" con "mi API es segura".

---

## La postura honesta

| Lo que el módulo ES | Lo que el módulo NO es |
|---------------------|------------------------|
| Enseñanza de los 7 métodos de autenticación + buenas prácticas 2026 en las capas que toca (hash, firmas, cookies, rate limit, headers) | Una aplicación "lista para producción" que mitiga las 10 categorías del Top 10 |
| Autenticación: "¿quién sos?" | Autorización: "¿qué podés hacer?" (eso es A01 → Nivel 03, próxima clase) |
| Un ejemplo autocontenido (memoria, demo user) | Un sistema con usuarios reales, MFA, auditoría, etc. |

**La lección de fondo**: un backend de autenticación bien hecho es una pieza
de un rompecabezas de seguridad. La seguridad real es **de defensa en
profundidad**: network, TLS, headers, WAF, rate limit, auth, authz, logging,
monitoreo. Cada capa cubre lo que las otras no ven.

---

## Mapeo por categoría (2021 → 2026)

| # | Categoría | Estado en el módulo | Dónde / evidencia | Qué harías en producción real (cerrar la brecha) |
|---|-----------|---------------------|-------------------|--------------------------------------------------|
| A01 | **Broken Access Control** | 🔴 **NO cubierto** *(es Nivel 03)* | No hay roles, no hay scopes. Cualquier usuario autenticado llega a `/me`. | RBAC (roles + permisos), scopes reales en OAuth, validar `sub`+rol en CADA endpoint, deny-by-default. **Eso es el proyecto de la próxima clase.** |
| A02 | **Cryptographic Failures** | 🟢 **Bien cubierto** | `security.py`: Argon2id (`PasswordHash.recommended()`), `algorithms=[ALGORITHM]` explícito, `secrets.token_urlsafe(32)`, `timezone.utc` en exp. | Secret manager (Vault/AWS KMS) para SECRET_KEY, TLS 1.2+ obligatorio (HSTS ya lo agregamos), rotación de claves, `pyjwt` actualizado (dependabot). |
| A03 | **Injection** | ⚪ **N/A (pero ojo)** | Storage en memoria, sin SQL. | Con SQL real: ORM (SQLModel/shema) con queries parametrizadas, NUNCA f-strings en SQL. Validar input con Pydantic (ya lo hacemos: `EmailStr`). |
| A04 | **Insecure Design** | 🟡 **Parcial** | `docs/CASOS_DE_USO.md`: diseño guiado por seguridad (amenazas → decisiones). | Threat modeling formal (STRIDE) antes de codear, casos de abuso como criterio de aceptación, PRs con checklist de seguridad. |
| A05 | **Security Misconfiguration** | 🟢→🟡 **Mejorado en Nivel 02** | `middleware.py` (HSTS, nosniff, X-Frame, Referrer, no-store), `COOKIE_SECURE` config-driven, `SECRET_KEY` fail-loud. | CORS restringido a orígenes conocidos, headers también en reverse proxy/WAF, `Security.txt`, versionado visible, debug off. |
| A06 | **Vulnerable & Outdated Components** | 🟡 **Parcial** | Stack actual (pwdlib, pyjwt); docs avisan contra passlib/python-jose. | `uv sync` + `uv lock` (ya está el lockfile), dependabot/renovate activos, escaneo de vulnerabilidades (trivy/snyk), SBOM. |
| A07 | **Identification & Auth Failures** | 🟢→🟡 **El corazón, reforzado en Nivel 02** | Timing attack (`DUMMY_HASH`), mensajes genéricos, httpOnly+SameSite, **rate limiting nuevo (5 fallos → 429)**. | **Falta (siguiente paso real)**: MFA (TOTP), lockout/ban, prevención de credential stuffing (haveibeenpwned), session fixation hardening, CSRF tokens explícitos, políticas de contraseña y breach lists. |
| A08 | **Software & Data Integrity** | 🟢 **Bien cubierto** (parcial) | Verificación de firma JWT + `iss`/`aud`/`exp` (SSO), `uv.lock` para dependencias. | Firmas en updates/release (cosign), pinning exacto de versiones, checksum de artifacts, CI con verificación de origen. |
| A09 | **Logging & Monitoring Failures** | 🔴 **NO cubierto** | No hay logging de eventos de seguridad. | `logging` estructurado (JSON) de logins exitosos/fallidos, logout, 429s; correlación con trazas; alertas en SIEM (Splunk/Sentry/Grafana); retención y protección de logs. |
| A10 | **SSRF** | ⚪ **N/A** | No hay fetching de URLs del usuario. | Si agregás features que piden URLs: allowlist de dominios, validación de DNS/IP privadas, no seguir redirects a ciegas. |

---

## Lo que el módulo enseña sobre TIEMPO real

Los ataques de autenticación más comunes en producción y cómo este módulo los
mitiga (o no):

| Ataque real | ¿Mitigado? | Cómo |
|-------------|-----------|------|
| **Brute force / credential stuffing** | 🟢 Nivel 02 | Rate limiting por email: 5 fallos → 429 (`app/rate_limit.py`) |
| **Timing attack** (enumerar emails) | 🟢 | `DUMMY_HASH`: "email no existe" tarda lo mismo que "password mal" |
| **XSS roba el token** | 🟢 | Cookies `httpOnly` (métodos 2 y 5) |
| **CSRF** (cookie viaja sola) | 🟡 | `SameSite=lax` + headers. El NEXT: token CSRF explícito |
| **Algorithm confusion** en JWT | 🟢 | `algorithms=[ALGORITHM]` explícito en `decode_token` |
| **Token swapping** (token de otra app) | 🟢 | Validación `aud`/`iss` en SSO (método 7) |
| **Password spray** (mismo pass en muchas cuentas) | 🔴 **NO** | Se mitiga con rate limit por IP + MFA + breach lists (próximo nivel) |
| **Credenciales en logs** | 🟡 | El header `Authorization` no se loguea acá; en prod: filtrar en logging |

---

## Cómo se hace en un proyecto real (el "deber ser")

El camino de producción para una API FastAPI autenticada, capa por capa:

```
┌─ Capa 1 · Red / Infra ────────────────────────────────────────────
│  TLS 1.2+ (HSTS), reverse proxy (nginx/traefik), WAF (Cloudflare),
│  rate limit por IP a nivel gateway, allowlist de orígenes CORS
├─ Capa 2 · App (lo que viste en este módulo + lo que falta) ───────
│  Argon2id · JWT firmado con algorithms explícito · iss/aud/exp ·
│  cookies httpOnly+SameSite+Secure · rate limit login · headers ·
│  timing attack · mensajes genéricos · validación de input
├─ Capa 3 · Autorización (≠ autenticación) ─────────────────────────
│  RBAC (roles/permisos), scopes OAuth reales, deny-by-default,
│  tenancy (cada usuario ve solo sus datos)  ← PRÓXIMA CLASE
├─ Capa 4 · Cuentas & identidad ────────────────────────────────────
│  MFA (TOTP/WebAuthn), lockout, breach-list checks, recovery,
│  políticas de password, session fixation hardening, CSRF tokens
├─ Capa 5 · Observabilidad ─────────────────────────────────────────
│  Logging estructurado de eventos de seguridad, auditoría,
│  alertas (SIEM/Sentry), métricas (Prometheus) de fallos de login
└─ Capa 6 · Operaciones ────────────────────────────────────────────
   Rotación de secretos, dependabot, escaneo de vulnerabilidades,
   backups cifrados, plan de respuesta a incidentes
```

> Cada capa es un curso entero. Ningún proyecto real "termina" el Top 10:
> se mantiene el riesgo bajo y se monitorea lo que queda.

---

## Qué queda para la próxima clase (Nivel 03)

**Autorización — RBAC, scopes y tenancy.** Cierra A01, que es la #1 del Top 10
desde 2021. Incluye:

1. Roles (admin, editor, viewer) y permisos por endpoint.
2. Scopes reales en OAuth2 (no solo `read:profile` de juguete).
3. Deny-by-default: si no hay regla → 403.
4. Multi-tenancy: un usuario de la empresa A no puede ver datos de la B.
5. Integración con el SSO real de la universidad (Keycloak/Google) para
   validar la teoría de este módulo contra un IdP de verdad.

Ese es el proyecto práctico que sigue. Con el Nivel 01 (este documento) y el
Nivel 02 (rate limit + headers + fail-loud + COOKIE_SECURE), ya sabés
**qué** falta y **por qué** — te falta solo el "cómo", y eso lo vemos
código en mano.

---

## Checklist definitiva

- [ ] Leí el mapeo completo y entiendo QUÉ cubre y QUÉ no cubre este módulo.
- [ ] Sé que autenticación (A07) ≠ autorización (A01).
- [ ] Puedo explicar por qué "a prueba de OWASP" es una meta, no un estado.
- [ ] Puedo decir qué 3 brechas cerraría PRIMERO en un proyecto real.
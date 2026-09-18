# Casos de Uso — Diseño guiado por seguridad

> Este documento NO te dice "usá JWT". Te enseña a **pensar como arquitecto de
> seguridad**: dado un contexto, ¿qué combinación de dimensiones elegís y por
> qué? La respuesta siempre arranca con la pregunta correcta.

---

## La pregunta que abre todo

> **¿Cuál es el daño potencial si roban esta credencial?**

Todo el diseño cuelga de esa respuesta. Si el daño es chico (leer tu perfil
público) podés usar Basic con HTTPS. Si el daño es enorme (transferir dinero,
borrar producción), necesitás revocación inmediata, MFA, y un IdP.

---

## Caso 1 · API interna de monitoreo

**Contexto**: un script de dashboards consulta `/api/metrics`. Es interno, red
de la empresa, tráfico bajo. Los desarrolladores también prueban endpoints a
mano.

**Decisión**: `Basic Auth` sobre HTTPS.

**Por qué**:
- No hay usuarios reales, no hay logout, no hay sesión.
- La revocación no importa: se rota una credencial compartida.
- Un token (JWT u opaco) agrega infraestructura que no aporta nada acá.

**Contraindicado**: JWT (¿para qué firmar si es interno?), session (¿para qué
guardar estado?), OAuth2 (¿delegación de qué?).

> ⚠️ La condición *sine qua non*: **nunca** la password real de un usuario, y
> **siempre** HTTPS. Y el header `Authorization` no debe loguearse.

---

## Caso 2 · Web app clásica (form de login server-rendered)

**Contexto**: panel de administración con formulario de login, HTML generado
por el server, sin SPA. El usuario cierra el browser y espera que lo desloguee.

**Decisión**: `Session Based` con cookie `httpOnly` + `SameSite=Strict` +
CSRF token, y sesión en el server.

**Por qué**:
- El "logout al cerrar el browser" y la revocación inmediata son naturales con
  estado en el server (sesión expira / se borra).
- La cookie `httpOnly` evita que el JS robe la sesión (XSS no la puede leer).
- `SameSite=Strict` + CSRF token mitigan el riesgo de CSRF.

**Tradeoff asumido**: el server guarda sesiones (memoria o Redis). Escalar
implica escalar ese storage. Es el precio de la revocación inmediata.

**Contraindicado**: JWT en header con una SPA (no hay SPA), Basic (sin
concepto de logout), token opaco (la cookie es más natural acá).

---

## Caso 3 · SPA moderna + API (React/Vue) con equipo chico

**Contexto**: frontend en SPA, API REST separada, CORS, sin backend server-
side. El equipo no quiere administrar Redis.

**Decisión**: `JWT en cookie httpOnly` (método 5) + CSRF token, **o** JWT en
header con token en memoria del JS. La primera es más segura de base.

**Por qué**:
- El equipo quiere stateless: sin storage de sesión, escalar es gratis.
- Con cookie `httpOnly`, el token no está expuesto a XSS.
- TTL corto (30 min) + refresh token rotado: si roban el access token, la
  ventana de daño es chica.

**Tradeoffs**:
- ❌ No podés revocar un JWT robado antes de que expire (deny-list opcional).
- ❌ CSRF: la cookie viaja sola en requests → `SameSite` + token anti-CSRF.

**Contraindicado**: session (quiere estado que no quiere mantener), token
opaco (idéntico problema de storage que sessions), OAuth2 password flow en la
SPA (el secreto de cliente no puede vivir en el browser — eso es el Anti-Pattern).

> 🔴 **Anti-Pattern famoso**: guardar el JWT en `localStorage`. Cualquier XSS
> lo lee. Con cookie httpOnly, el XSS no lo toca. Priorizá cookie.

---

## Caso 4 · App móvil + API propia

**Contexto**: Android/iOS consumen tu API. No hay cookies en móviles.

**Decisión**: `OAuth2 password flow` (login con email/password) → `JWT
short-lived (15-60 min)` + `refresh token` con rotación.

**Por qué**:
- El móvil no tiene la ergonomía de cookies → Bearer header.
- El access token corto minimiza el daño si se filtra.
- El refresh token vive en el secure storage del OS (Keychain/Keystore), no en
  el código.

**Tradeoffs**:
- Manejar refresh tokens es infraestructura (tabla, rotación, revocación).
- El refresh token también se puede robar → detectar rotación (reuso = revocar).

**Contraindicado**: Basic (la app repetiría la password en cada request),
JWT de larga duración (no revocable), session en cookie (no hay cookies).

---

## Caso 5 · Microservicios internos (servicio a servicio)

**Contexto**: 10 servicios hablan entre sí. No querés que cada uno consulte
una base de usuarios.

**Decisión**: `JWT` firmado por un gateway/auth-service, validado en cada
servicio **solo por firma** (stateless), con `iss`/`aud`/`exp` validados.

**Por qué**:
- Sin estado compartido: cada servicio valida la firma localmente.
- `aud` evita ataques de *token swapping* (un token de servicio A no vale en B).
- El gateway emite tokens cortos; los servicios no conocen passwords.

**Tradeoffs**:
- Revocación casi nula: si el gateway está comprometido, los tokens viven
  hasta expirar → rotación de la key del gateway + TTL corto.
- Key management: rotación de claves de firma (JWKS).

**Contraindicado**: session (cada servicio tendría que compartir el storage),
Basic (¿password de servicio en cada request? no), OAuth2 password flow.

---

## Caso 6 · Login único entre apps de la empresa (SSO)

**Contexto**: 5 aplicaciones (web, móvil, admin) y RRHH quiere "un solo login".

**Decisión**: `SSO / OIDC` con IdP central (Keycloak, Okta, Entra ID, Couso,
Google Workspace). Cada app valida `id_token` con `iss` + `aud` + `exp`.

**Por qué**:
- El usuario se loguea UNA vez; las apps no guardan passwords.
- JIT provisioning: el usuario se crea en la app en el primer login.
- MFA lo maneja el IdP, no cada app.

**Tradeoffs**:
- Dependés de un tercero (disponibilidad, y "si se cae, no entra nadie").
- Complejidad: well-known, JWKS, flujos PKCE.

**Contraindicado**: cada app con su propia tabla de passwords (el problema que
justamente querés resolver).

> Lo vimos funcionando: `/api/sso/simulate` emite un `id_token` y `/api/me/sso`
> valida `iss` + `aud`. Un JWT *local* (sin `iss`/`aud` del IdP) es rechazado
> con 401. Ese es el patrón real, sin el código del IdP.

---

## Caso 7 · Integraciones externas (bots, scripts, CI/CD)

**Contexto**: una empresa externa o un bot necesita acceso a tu API sin un
usuario humano.

**Decisión**: `Token opaco` por integración (revocable) con scopes.

**Por qué**:
- Cada integración tiene SU token → revocar uno no afecta a las demás.
- Scopes limitan lo que cada integración puede hacer (principio de menor
  privilegio).
- El token se rota cuando se va el proveedor (sin tocar usuarios).

**Contraindicado**: une sola password compartida (no hay granularidad),
Basic (password propagada), JWT de larga vida (no revocable).

---

## La herramienta mental: árbol de decisión

```
¿Quién consume?
│
├── Browser
│   ├── ¿Server-rendered?        → Session cookie + SameSite + CSRF
│   └── ¿SPA?                    → JWT en cookie httpOnly + CSRF, o JWT en header
│                                 (memoria JS) con refresh rotado
│
├── Móvil                        → OAuth2 password flow + JWT corto + refresh
│
├── Servicio (backend)           → JWT firmado por gateway (iss/aud) o mTLS
│
├── Script / bot / integración   → Token opaco revocable + scopes
│
└── Monitoreo interno            → Basic Auth sobre HTTPS (credencial rotable)
```

El diagrama no reemplaza la pregunta inicial (¿daño potencial?), pero te
encamina.

---

## Checklist de seguridad (para cualquier diseño)

- [ ] ¿HTTPS en TODOS los entornos? (incluido dev)
- [ ] ¿La password viaja en el body/request y se hashea con **Argon2id** en el server?
- [ ] ¿El `Authorization` header está excluido de los logs?
- [ ] ¿Los tokens tienen **expiración corta** y el algoritmo de firma es explícito?
- [ ] ¿Validás `iss`, `aud`, `exp` en TODA decodificación de JWT?
- [ ] ¿Las cookies son `httpOnly` + `Secure` + `SameSite`? (`COOKIE_SECURE=true` en prod)
- [ ] ¿La revocación es posible en el plazo que el riesgo exige?
- [ ] ¿Aplicaste **menor privilegio** (scopes/roles) por integración y usuario?
- [ ] ¿El timing de login es indistinguible para usuarios existentes/inexistentes (DUMMY_HASH)?
- [ ] ¿El login tiene **rate limiting / lockout** (5 fallos → 429)? Y en multi-instancia, ¿vive en un almacén compartido (Redis) o gateway?
- [ ] ¿Hay **security headers** (HSTS, nosniff, X-Frame-Options, Referrer-Policy) y `Cache-Control: no-store` en rutas con datos del usuario?
- [ ] ¿`SECRET_KEY` sale de un secret manager / env var y falla ruidosamente si falta en producción? (nunca un default silencioso)
- [ ] ¿El código NO usa `passlib`/`python-jose`/`hashlib-plano`?

> **Recordá**: la autenticación (A07) es "¿quién sos?". La autorización (A01)
> es "¿qué podés hacer?" — y es la brecha #1 del OWASP Top 10. Este checklist
> NO termina ahí: roles, scopes y tenancy son la próxima clase (Nivel 03).

Si alguna respuesta es "no", sabés qué tenés que justificar en el PR. 😉
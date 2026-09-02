# 🧭 Guía del Docente — Autenticación y Seguridad

> **Módulo 04 — Desarrollo de Software 2026**
> **Metodología**: aula invertida + taller por grupos con descubrimiento
> **Duración**: 60 minutos de **actividad** (la lectura previa es aparte — no cuenta en los 60)
> **Tu rol**: no dictás — guiás, desbloqueás y hacés preguntas.

---

## 1. La idea en una frase

El Módulo 03 terminó con una API de tareas que **cualquiera puede tocar**.
Cualquiera borra, cualquiera edita, cualquier tarea es de todos. Hoy la
pregunta es: *"¿cómo le decimos al sistema QUIÉN es el que está hablando, y
que solo haga lo que tiene permitido?"*.

La lección de fondo no es "usar JWT". Es entender que hay **tres preguntas
distintas** que la gente confunde todo el tiempo:

| Pregunta | Respuesta | Módulo |
|----------|-----------|--------|
| ¿Quién sos? | **Autenticación** (login, register) | hoy |
| ¿Qué podés hacer? | **Autorización** (roles, permisos) | hoy (conceptual) + futuro RBAC |
| ¿Cómo lo demuestro en cada request? | **Sesión vs token** | hoy (la discusión clave) |

---

## 2. El análisis de diseño (por qué está armado así)

Este módulo sigue el patrón del 03 (aula invertida + descubrimiento), con
una decisión de alcance **Opción B + Argon2**:

### 2.1 Por qué Opción B (con scaffold de código)

La seguridad **no se aprende leyendo**: se aprende escribiendo el código
vulnerable y viendo POR QUÉ está mal. Por eso el scaffold entrega el esqueleto
y los alumnos completan las piezas de la lección, no leen sobre ellas.

### 2.2 Por qué Argon2 (y no bcrypt ni passlib)

- **Argon2** es el ganador del Password Hashing Competition (2015) y el
  estándar actual. Es resistente a GPU/brute-force por diseño (parametrizable
  en memoria y tiempo).
- La doc oficial de FastAPI **hoy recomienda `pwdlib`** (`PasswordHash.recommended()`
  → Argon2id), reemplazando a `passlib` (mantenimiento en duda) y `python-jose`
  (obsoleto). Es lo que se usa en producción en 2026.

### 2.3 Las dos trampas conceptuales que NO hay que regalar mal

1. **SSO y JWT no son comparables.** SSO es un *flujo* de autenticación
   delegada (SAML, OIDC/OAuth2). JWT es un *formato* de token. Son
   ortogonales: un SSO casi siempre **emite un JWT**. "SSO vs JWT" es como
   comparar "el sistema de riego" con "el tipo de caño".

2. **La sesión server-side y el JWT tienen un tradeoff real, no un ganador:**
   sesión = revocación fácil + estado en el server (escala con Redis/DB
   compartida); JWT = stateless + escala horizontal fácil + **revocación
   difícil** (esperar `exp` o blacklist).

### 2.4 La lección transversal (continuidad con el 03)

El `404` del Módulo 03 vivía en el controller porque era HTTP. Hoy la lección
es **gemela**: el `401`/`409` también viven en la capa HTTP; el hash y la
firma viven en `security.py` (que no sabe de HTTP); el service devuelve `None`
y no lanza status codes. Es el MISMO principio aplicado a la seguridad.

---

## 3. Antes de la clase (aula invertida)

1. **Asigná** [`MATERIAL_PREVIO.md`](./MATERIAL_PREVIO.md) con 3-4 días de
   anticipación. Dejá claro que es taller y sin lectura no van a poder construir.
2. **Verificá** la lectura con un quiz de 3 preguntas (en la presentación).
   No es evaluación: activa y detecta quién no leyó.
3. **Prepará el scaffold**: el repo ya tiene el código completo. Para el
   taller entregás la versión **incompleta** (los 6 archivos con TODO). La
   solución completa va en una rama `solucion` que desbloqueás al final.

> 💡 **Consejo**: guardá el código completo en la rama `solucion`. Los alumnos
> trabajan en su fork con el esqueleto; al final hacen `git diff main..origin/solucion`.

---

## 4. Los grupos (ya están formados)

Cada grupo en **una sola máquina** (pair/ensemble). Roles rotativos:

| Rol | Hace |
|-----|------|
| **Piloto** | Escribe el código (comparte pantalla) |
| **Navegante** | Lee la consigna y las pistas, anticipa errores |
| **Investigador** | Busca en la doc/memorias del Módulo 03 o en la bibliografía |

Rotá en cada fase (Security → Repository → Service → Controller). Así todos
tocan teclado y todos razonan.

---

## 5. El tiempo en el aula: apertura + 60 minutos de actividad

La **lectura previa** NO cuenta en los 60. Los 60 son **solo actividad**.

### Apertura — verificación de lectura previa (fuera de los 60)

| ~min | Qué hacés |
|------|-----------|
| 0-5 | **Quiz de 3 preguntas** — verificá quién leyó |
| 5-15 | **Repaso relámpago**: autenticación vs autorización → hash → sesión vs JWT → SSO vs JWT → OWASP. Sin profundizar: ya lo leyeron |

### Actividad — 60 minutos

| Min | Fase | Qué hacés vos | Qué hacen los grupos |
|-----|------|---------------|----------------------|
| 0-5 | **Setup** | Entregá scaffold, verificá `uv sync` + `.env` + server | Levantan, ven `/docs`, saludan al health |
| 5-20 | **Security** | Desbloqueás con preguntas ("¿el token se firma o se encripta?"). Checkpoint 1 | Completan hash + JWT (4 funciones) |
| 20-30 | **Repository** | "¿el repository hashea? ¿por qué no?" | Completan los 3 métodos |
| 30-40 | **Service** | El momento clave: la pregunta del `None` vs `401` | Completan register + authenticate |
| 40-55 | **Controller + get_current_user** | Guiás la traducción `None` → `401/409`. Checkpoint 2 | Completan endpoints + la dependencia que protege |
| 55-60 | **Frontend + cierre** | "Levanten `pnpm dev` y hagan el ciclo completo" | Conectan el frontend: register → login → perfil |

> ⏱️ **No te aferres al reloj.** Los checkpoints importan más que los minutos.
> Si un grupo se atrasa, priorizá que lleguen al **Checkpoint 2** (flujo
> register → login → /me andando).

---

## 6. Checkpoints (dónde parar y verificar)

**Checkpoint 1 — Security andando (min ~20 de actividad)**
```bash
curl http://localhost:8000/api/health   # users_count: 0
uv run python -c "from app.security import hash_password, verify_password; h=hash_password('x12345678'); print(h[:11]); print(verify_password('x12345678',h))"
# → $argon2id$v=  y  True
```
El grupo tiene hash + verify + token funcionando.

**Checkpoint 2 — Flujo completo (min ~55 de actividad)**
```bash
curl -X POST http://localhost:8000/api/auth/register -H "Content-Type: application/json" -d '{"email":"juan@ejemplo.com","password":"supersecreto123"}'
curl -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d '{"email":"juan@ejemplo.com","password":"supersecreto123"}'
curl http://localhost:8000/api/users/me -H "Authorization: Bearer <TOKEN>"
curl http://localhost:8000/api/users/me   # → 401
```
Register devuelve `201` sin hash; login devuelve token; `/me` con token devuelve el user; sin token `401`.

**Checkpoint 3 — Frontend integrado (min ~60 de actividad)**
El frontend en `:5173` hace el ciclo completo: register → login → perfil →
logout. El token viaja en `Authorization: Bearer`.

---

## 7. La reflexión final (no la saltees)

Cerrá con estas preguntas al grupo entero (5 min, responden en voz alta):

1. **"¿Dónde guardamos la contraseña y por qué?"** → esperá: "un hash Argon2,
   nunca texto plano; porque las bases se filtran".
2. **"¿Dónde vive el 401 y por qué no en el service?"** → porque 401 es HTTP,
   el service devuelve `None`. Si responden "en el controller / get_current_user",
   ya entendieron. Es el 404 del Módulo 03, aplicado a seguridad.
3. **"¿El JWT se encripta o se firma? ¿Qué implica?"** → se firma. El payload
   es legible → nada de secretos adentro.
4. **"¿Por qué el login devuelve un mensaje genérico?"** → para evitar user
   enumeration (no revelar si el email existe).
5. **"¿SSO vs JWT?"** → pregunta trampa: no se comparan. SSO es flujo, JWT es
   formato. Un SSO emite un JWT.
6. **"¿Dónde guardaste el token en el frontend y qué riesgo trae?"** →
   `localStorage` en la demo; riesgo XSS. En producción se evalúa cookie
   `httpOnly` + CSRF. Dejá que lo discutan.

Terminá con la frase: *"Hoy no agregaron un login — le pusieron una identidad
a cada request, y una puerta a la API."*

---

## 8. Síntomas comunes (y cómo desbloquear)

| Síntoma | Causa probable | Desbloqueo |
|---------|----------------|------------|
| `ModuleNotFoundError: app` | Corren desde el directorio equivocado | Están en `backend/` y ejecutan `uv run -m app.main` |
| `ImportError: jwt` / `pwdlib` | No corrieron `uv sync` | `uv sync` instala pyjwt, pwdlib[argon2], email-validator |
| `422` al registrar email raro | `EmailStr` rechaza emails mal formados | Es correcto: valida formato. Probá con un email válido |
| `409` al registrar dos veces | El email ya existe (constraint unique) | Es lo esperado: probá con otro email |
| `401` en `/me` con token | Token no pegado como `Bearer <token>`, o expirado | Revisá el header exacto y que el token no haya expirado |
| Token "firma inválida" | Modificaron un char del token | Correcto: la firma detecta alteraciones. Probalo |
| No saben dónde va el hash | Confusión de capas | *"¿hashear es HTTP, datos, negocio o criptografía?"* → seguridad |
| No saben si el service lanza 401 | Misma confusión del 03 | *"¿el service sabe qué es un status code?"* → No, devuelve `None` |
| `datetime.now()` sin timezone | Huso horario | *"¿calculaste la expiración con timezone.utc?"* |
| `jwt.decode` sin `algorithms` | Algorithm confusion attack | *"¿qué algoritmos permitís decodificar?"* → siempre explícito |

---

## 9. Ejercicios de cierre (para casa)

- 🟢 Explicá con tus palabras la diferencia entre autenticación y autorización,
  y el tradeoff sesión server-side vs JWT.
- 🟡 Agregá expiración personalizable al login (parámetro opcional de minutos)
  y mostrá el `exp` decodificado del token en `jwt.io`.
- 🔴 Implementá la mitigación del timing attack: cuando el usuario no existe,
  verificá contra un hash falso (`hash_password("dummy")`) para que el tiempo
  de respuesta sea constante. Investigá por qué importa.
- 🔴 Investigá cómo revocar un JWT (blacklist en Redis) y qué tradeoff
  reintroduce. ¿Cuándo conviene una sesión server-side?

---

> **Recordá**: el objetivo no es que terminen el login. Es que **entiendan por
> qué** cada pieza existe. Si se traban y les das la respuesta, se llevan
> código. Si los guiás con preguntas, se llevan el criterio.

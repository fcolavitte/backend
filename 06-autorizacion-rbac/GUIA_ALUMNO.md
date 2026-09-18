# Guía del Alumno — Autorización RBAC (entrega individual)

> **Módulo 06 — Desarrollo de Software 2026**
> **Modalidad**: aula invertida + entrega individual obligatoria.
> Ya leíste el `MATERIAL_PREVIO.md` y la `SPEC.md`. Ahora a construir.

---

## Cómo funciona esta entrega

1. Tu **fork** trae el backend casi listo: solo completás **4 archivos**
   (3 de backend + 1 del frontend).
2. Cada fase te lleva a un archivo, con consignas de descubrimiento.
3. Al final de cada fase corrés el **script de verificación** y mirás qué
   checks se ponen verdes.
4. **Si te trabás**: releé la SPEC (la sección "La spec de tu entrega").
   El docente en la defensa NO te da la respuesta — te hace preguntas
   que te ayudan a descubrirla.

> 🎯 **Tu meta**: `bash scripts/verificar_authz.sh` → **44/44 checkpoints OK**,
> la **consola del frontend coherente** con la matriz, y poder explicar
> cada 403 de tu código en la defensa oral.

---

## Qué ya viene hecho (NO se modifica)

```
06-autorizacion-rbac/backend/app/
├── models.py            ✅ dado
├── db.py                ✅ dado (engine + tablas SQLModel, PostgreSQL)
├── storage.py           ✅ dado (seed idempotente: 2 tenants, 4 users, 5 docs)
├── config.py            ✅ dado
├── security.py          ✅ dado (hash + JWT con claims role/tenant/scope)
├── auth_common.py       ✅ dado (verify_login)
├── auth_controller.py   ✅ dado (register + login con scope)
├── dependencies.py      ⬅️ FASE 1 (require_role + require_scope)
├── controllers/
│   ├── users_controller.py     ⬅️ FASE 2 (3 endpoints)
│   └── documents_controller.py ⬅️ FASE 3 (6 endpoints)
└── main.py              ✅ dado

06-autorizacion-rbac/frontend/src/
└── authz.ts             ⬅️ FASE 4b (6 helpers de autorización en la UI)
```

---

## Fase 0 — Setup (5 minutos)

```bash
# 1) La base de datos (service postgres del compose — la PERSISTENCIA)
docker compose up -d postgres

# 2) El backend con uv (apunta al mismo postgres, localhost:5432)
cd 06-autorizacion-rbac/backend
uv sync                  # instala las dependencias en .venv (incluye sqlmodel)
uv run -m app.main       # arranca en :8000
```

Verificá:

```bash
curl http://localhost:8000/api/health
# → {"status":"Funciona","users_count":4,"documents_count":5,"tenants_count":2}
```

> 💡 El server arranca con el dataset sembrado SOLO la primera vez: los
> usuarios y documentos viven en PostgreSQL y **persisten** entre reinicios.
> No hace falta ningún registro manual, y reiniciar NO borra nada.

---

## Fase 1 — `dependencies.py`: las llaves de la autorización (20 min)

**Objetivo**: completar `require_role` y `require_scope`. Son dos "factories"
de dependencias: reciben un argumento y devuelven una función `checker`
que FastAPI usa como dependencia.

### ¿Cómo están? (mirálas ANTES de tocar)

```python
def require_role(required: Role):
    def checker(current_user=Depends(get_current_user)):
        return current_user      # ← 🔴 SIN VERIFICAR: cualquiera pasa
    return checker
```

Ahora mismo, **cualquier autenticado** puede listar usuarios, cambiar roles
y borrar documentos. Probalo (si el server está arriba):

```bash
# Logueate como viewer (solo lectura) y mirá lo que PODÉS hacer:
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"viewer@acme.com","password":"demo12345"}' \
  | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

curl http://localhost:8000/api/users -H "Authorization: Bearer $TOKEN"
# → 200 con la lista de usuarios... UN VIEWER VIENDO TODOS LOS USUARIOS. 💥
```

**Esto es Broken Access Control (OWASP A01). Tu trabajo: cerrarlo.**

### Consigna 1 — `require_role`

1. Compará `current_user.role` con `required`. ¿Coinciden?
2. NO → `raise HTTPException(status_code=403, detail="No tenés el rol necesario para esta operación")`
3. SÍ → `return current_user`

### Consigna 2 — `require_scope`

1. Leé el scope del TOKEN desde el estado que dejó `get_current_user`:

```python
payload = request.state.token_payload
token_scope = payload.get("scope", "")
```

2. ¿`required` está entre los scopes del token? (pensá en `.split()`:
   el scope del token puede ser `"read"` o `"read write"`).
3. NO → `raise HTTPException(status_code=403, detail="El token no tiene el scope necesario para esta operación")`
4. SÍ → `return current_user`

> 🧠 **La pregunta que te va a caer en la defensa**: ¿por qué el rol se
> relee de `storage` y el scope se lee del token? (pista: ¿qué pasa si un
> admin degrada a alguien? ¿su token viejo sigue valiendo?).

### Verificá la fase

Después de completar la Fase 1, corré el script (necesitás el server arriba):

```bash
bash scripts/verificar_authz.sh
```

Van a ponerse verdes los checks de **"NO puede listar usuarios"**,
**"NO puede cambiar roles"** y **"admin con token read-only NO puede crear"**.
Los de documento (IDOR) siguen rojos — es la Fase 3.

---

## Fase 2 — `users_controller.py`: solo admin, solo su empresa (15 min)

**Objetivo**: proteger los 3 endpoints de usuario. La matriz exige:
**solo admin** y **solo de su propia empresa**.

### Consigna 1 — `list_users`

El endpoint hoy usa `Depends(get_current_user)`. El check del script dice
que un viewer NO debe poder listar usuarios. ¿Qué dependencia usás en
reemplazo? (pista: está en la tabla de la SPEC, sección 3.2).

> 🧠 Notá que el cuerpo ya filtra por tu tenant
> (`storage.list_users(tenant_id=current_user.tenant_id)`): el storage
> nunca devuelve usuarios de otra empresa. Tu trabajo es el ROL.

### Consigna 2 — `get_user`

El endpoint ya tiene `require_role(Role.ADMIN)`. Pero falta el **tenancy**:
un admin de Acme NO debe poder ver a admin@globex.com. Agregá el check:

```python
if user.tenant_id != current_user.tenant_id:
    raise HTTPException(403, "No podés ver usuarios de otra empresa")
```

> 🧠 Orden de los checks: 404 primero (no existe), 403 después (existe pero
> no te corresponde). ¿Por qué funciona ese orden? (defensa oral).

### Consigna 3 — `change_role`

El más sensible: cambiar el rol de un usuario. Tenés DOS check que hacer:
el rol (¿sos admin?) y el tenancy (¿es de tu empresa?). Mirá cómo está
implementado y agregá lo que falta.

> 🧠 Pregunta de la defensa: ¿qué pasa si un admin le cambia el rol a otro
> mientras el otro tiene un JWT activo? Pensá en el diseño elegido: el rol
> se relee de storage en cada request → el cambio es INMEDIATO.

### Verificá la fase

```bash
bash scripts/verificar_authz.sh
```

Los 7 checks de "gestionar usuarios" deberían ponerse verdes.

---

## Fase 3 — `documents_controller.py`: el IDOR (25 min)

**Objetivo**: cerrar el ataque más común del OWASP A01. Ahora mismo:

```bash
# viewer (solo lectura) pide el "Plan secreto Globex" (#5)...
curl http://localhost:8000/api/documents/5 -H "Authorization: Bearer $TOKEN"
# → 200. LEE EL PLAN SECRETO DE OTRA EMPRESA. 💥💥💥
```

Tres tipos de check en cada endpoint — usá la tabla de la SPEC (3.3):

### Consigna 1 — scope en los endpoints de escritura

`POST`, `PATCH`, `DELETE` y `POST /publish` modifican datos: exigen
`require_scope("write")`. Reemplazá `get_current_user` por la dependencia
correspondiente en cada uno.

> 🧠 Lección: un admin con token read-only NO puede crear, aunque su rol
> se lo permita. Scope del TOKEN ≠ rol del USUARIO.

### Consigna 2 — tenancy en TODO endpoint de documento

Cada endpoint mira si el documento es de la empresa del usuario:

```python
if doc.tenant_id != current_user.tenant_id:
    raise HTTPException(403, "No podés VER/EDITAR/BORRAR documentos de otra empresa")
```

> Importante: también en documentos PÚBLICOS. Un público de Acme no es
> visible para Globex. Tenancy por encima de todo.

### Consigna 3 — object-level (la más importante)

En `GET /documents/{id}`, `PATCH` y `POST /publish`:
después del tenancy, preguntate **¿dueño o admin?**

```
if doc.visibility == "public":      → devolvelo (ver)
if doc.owner_id == user.id:         → devolvelo/editalo/publicalo
if user.role == admin:              → devolvelo/editalo/publicalo (de su tenant)
else:                                → 403 "No podés ... este documento"
```

En `DELETE`, la matriz exige SOLO admin: agregá `require_role(ADMIN)` +
`require_scope("write")` en la firma.

> 🧠 Para el object-level leé el `current_user.role` del USUARIO (fresco),
> no del token. Así un admin recién degradado pierde el acceso al toque.

### Verificá la fase

```bash
bash scripts/verificar_authz.sh
# → ¡Esperemos 44/44!
```

---

## Fase 4b — Interfaz: alineá la UI con el server (frontend)

> ⚠️ Ojo con el orden: esta fase NO la podés hacer antes de la Fase 3.
> Primero el server tiene que responder los 403 reales; recién ahí la UI
> tiene algo contra qué alinearse. (Si la hacés antes, vas a "arreglar"
> la UI contra un server roto que responde 200 a todo — y cuando completes
> el backend te va a temblar la mano igual que la defensa oral.)

Levantá el frontend (terminal 2):

```bash
cd 06-autorizacion-rbac/frontend
pnpm install
pnpm dev
```

### La película de la alineación

1. **Antes (backend roto)**: la UI te muestra TODO habilitado — vista del
   viewer con botones de BORRAR y panel de USUARIOS. Clickleá: el server
   (roto también) responde 200. **Todo verde en la consola. Todo inseguro.**
   La UI "miente" igual que el server: ¡consistente!

2. **Backend arreglado (Fase 3), helpers sin tocar**: el server ahora
   responde 403 a lo que no corresponde... pero la UI SIGUE mostrando los
   botones. Clickleá BORRAR como viewer → 403 rojo en la consola. Ahí
   tenés la prueba viva: **ocultar un botón no es seguridad, y mostrarlo
   sin server ya no es mentira posible.** La UI quedó rota contra un
   server sano.

3. **Completás `authz.ts`**: los botones que el server rechaza desaparecen
   de la UI. Consola y matriz alineadas. La defensa oral te puede preguntar
   por qué la UI replica la matriz — y tu respuesta tiene que ser "UX
   honesta: no muestro una acción que el server va a rechazar, pero la
   SEGURIDAD está en el server".

### Qué completás

Un solo archivo: `frontend/src/authz.ts`. Son 6 helpers; la UI entera
(LoginPanel, DocumentsPanel, UsersPanel, ProberPanel) ya los usa:

| Helper | Matriz (SPEC 3.4) |
|--------|--------------------|
| `scopeAllowsWrite` | el TOKEN contiene "write" |
| `canManageUsers` | admin |
| `canChangeRole` | admin |
| `canDelete` | admin |
| `canEdit` | dueño o admin |
| `canPublish` | dueño o admin |

> 🧠 **Truco de verificación**: cada helper tiene que devolver lo mismo que
> responde el server. Probalo en el ProberPanel: el status HTTP vs. tu
> helper. Si se contradicen, uno de los dos está roto. Descubrir cuál es
> la mitad de la evaluación.

### Verificá la fase

```bash
pnpm build   # typecheck + build de un SPA que compila limpio
# y mirá la consola del frontend: 2xx verdes solo donde la matriz dice ✅
```

---

## Fase 4 — Defensa oral (definida por el resultado del script)

Según el resultado de la verificación, se agenda tu defensa oral individual
(5 min). Preparate para:

1. **Correr el script en vivo** y mostrar los checks verdes.
2. Explicar **tres decisiones de diseño** (tabla de la SPEC, sección 8):
   - ¿Por qué `401` ≠ `403` en tu código?
   - ¿Por qué el rol se lee de storage y el scope del token?
   - ¿Por qué el 404 va antes que el 403?
3. **Revisión de código**: con el resultado del script como guía, revisás
   tus implementaciones de `require_role`, `require_scope`, el object-level
   y los helpers de `authz.ts`.

> No memorices "la respuesta correcta". Entendé la PELÍCULA de un request:
> quién lo autentica, quién decide el rol, quién decide el ownership,
> y dónde cae cada 403.

---

## 🔐 La solución

La solución completa **NO está en este repo** y **no se libera antes de la
fecha de entrega** (22/09). Después de la entrega, se publica en la rama
`solucion` del repo base.

```bash
git fetch origin
git diff main..origin/solucion -- 06-autorizacion-rbac/
```

> **La gracia de la entrega está en descubrirlo vos.** Copiar sin entender
> te deja solo con un script que pasa y una defensa oral que no vas a poder
> sostener ni un minuto.
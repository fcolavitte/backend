# Material Previa — Autorización RBAC (lectura pre-clase)

> **Módulo 06 — Desarrollo de Software 2026**
> **Formato**: aula invertida. Leé este material ANTES de la clase.
> **Prerequisito**: haber hecho los módulos 04 y 05 (autenticación).

---

## 1 · La pregunta que falta: "¿qué podés hacer?"

Los módulos 04 y 05 te enseñaron a responder **"¿quién sos?"**:
con un JWT, una sesión o Basic Auth, la API sabe que sos `demo@ejemplo.com`.

Pero el Módulo 05 termina con una **brecha de seguridad que cerrar**:

```
¿Puede viewer@acme.com ver el "Estrategia 2026" (doc privado) de admin@acme.com?
→  SÍ. Si conocés el id, cualquier autenticado ve cualquier documento.
    Esto es **Broken Access Control** (OWASP A01 · #1 del Top 10 desde 2021).
```

**Autenticación (AuthN)** no es lo mismo que **Autorización (AuthZ)**:

| Dimensión | Pregunta | Lo que ve el usuario |
|-----------|----------|---------------------|
| **AuthN** | "¿quién sos?" | El JWT: `sub=1` → "soy admin@acme.com" |
| **AuthZ** | "¿qué podés hacer?" | Las REGLAS que deciden si podés acceder, modificar o borrar algo |

Un JWT solo te dice quién sos. **Decidir si HACER una acción es autorización.**
Confundir ambos es la fuente de los incidentes de seguridad más caros de la historia.

> **Lección clave**: `401` = "no sé quién sos" (AuthN). `403` = "sé quién sos,
> pero no tenés permiso para esto" (AuthZ). Un endpoint que devuelve `403`
> ESTÁ autenticando correctamente; es la AUTORIZACIÓN la que lo deniega.

---

## 2 · RBAC — Control de Acceso Basado en Roles

**RBAC** es el patrón más usado en la industria. La idea es simple:

```
1. Asignás un ROL a cada usuario (admin, editor, viewer).
2. Cada rol tiene PERMISOS (crear, editar, borrar, ver).
3. El endpoint verifica: "¿el rol del usuario tiene el permiso necesario?"
4. Si SÍ → ejecuta. Si NO → 403.
```

**REGLA DE ORO**: NUNCA asignás permisos directamente a usuarios sueltos.
Si "Juan" puede editar, no le das el permiso a Juan: le das el rol "editor"
a Juan, y el rol "editor" tiene el permiso "editar".

¿Por qué? Porque cuando tengas 50 usuarios, no revisás 50 permisos
individuales: revisás 3 roles y las reglas que asignás a cada uno.

### Los 3 roles de esta entrega

| Rol | Qué puede hacer |
|-----|-----------------|
| `admin` | Crear, editar, borrar CUALQUIER documento de su empresa. Gestionar usuarios (cambiar roles). |
| `editor` | Crear y editar sus propios documentos. Publicar lo suyo. NO borrar. |
| `viewer` | Solo VER documentos públicos. NO crear, NO editar, NO borrar. |

### ¿Cómo se implementa en FastAPI?

Con **dependencias reutilizables** (el patrón que ya conocés del módulo 04/05):

```python
from fastapi import Depends, HTTPException

def require_role(required: str):
    def checker(current_user = Depends(get_current_user)):
        if current_user.role != required:
            raise HTTPException(status_code=403, detail="No tenés el rol necesario")
        return current_user
    return checker

# Uso en un endpoint:
@app.delete("/api/documents/{id}")
def delete_doc(doc, current_user = Depends(require_role("admin"))):
    # Si no es admin, ya lanzó 403 antes de llegar acá.
    ...
```

---

## 3 · Object-level access control (el más violado)

RBAC te dice si el rol "puede". Pero un `editor` que crea un documento
**privado** no quiere que otro editor lo vea. ¿Cómo lo evitás?

```python
# MAL: el id lo conozco → lo veo
@app.get("/api/documents/{id}")
def get_doc(id, user = Depends(get_current_user)):
    return storage.get(id)    # ← BROKEN ACCESS CONTROL

# BIEN: verifico que el doc sea del usuario O que sea admin
@app.get("/api/documents/{id}")
def get_doc(id, user = Depends(get_current_user)):
    doc = storage.get(id)
    if doc.owner_id != user.id and user.role != "admin":
        raise HTTPException(403, "No podés ver este documento")
    return doc
```

Esto se llama **IDOR** (Insecure Direct Object Reference): "meto el id que
quiero y veo lo de otro". Es el ataque A01 más común del mundo real.

> **Pensalo**: si tu API tiene `GET /api/pedidos/123` y cualquiera que
> conozca el id lo accede, estás expuesto a IDOR. Eso es un bug de seguridad
> que OWASP cataloga como A01.

---

## 4 · Scopes: lo que el TOKEN puede hacer (distinto al rol)

El **rol** es del usuario (lo cambia un admin y es inmediato).
El **scope** es del token (lo fijó el login y vive hasta que expire).

```json
{
  "sub": "1",
  "role": "admin",
  "scope": "read write"
}
```

Si un admin genera un token de **solo lectura** (scope `"read"`) para una
integración externa, ese token NO debería poder crear documentos aunque
el usuario humano sea admin.

```python
def require_scope(required: str):
    def checker(request, current_user = Depends(get_current_user)):
        scope = request.state.token_payload.get("scope", "")
        if required not in scope.split():
            raise HTTPException(403, "El token no tiene el scope necesario")
        return current_user
    return checker
```

¿Dónde se usa? `require_role` dice "¿podés?" (del usuario). `require_scope`
dice "¿ESTE token puede?" (del token). Se combinan en los endpoints.

> **Pregunta para la clase**: si un admin loguea con scope "read" y crea un
> documento, ¿quién falla: require_role o require_scope? ¿Por qué el 403
> es el correcto (no el 401)?

---

## 5 · Multi-tenancy: cada empresa ve solo la suya

**Tenancy** es la separación de datos por organización/empresa.

```python
# SIEMPRE filtrar por el tenant del usuario autenticado
docs = [d for d in all_docs if d.tenant_id == user.tenant_id]
# NUNCA: return all_docs()  ← esto filtra TODO
```

En producción, un admin de empresa A **jamás** debería ver los datos de
empresa B. Y un admin de empresa A **jamás** debería poder gestionar los
usuarios de empresa B.

Esto se implementa con un filtro por `tenant_id` en TODA query, y con una
verificación en los endpoints de escritura (PATCH/DELETE) que comparan el
`tenant_id` del recurso contra el del usuario.

---

## 6 · Deny-by-default: si no hay regla, es 403

La regla más importante de seguridad: **si un endpoint no tiene dependencia
de autorización, es un BUG**.

```python
# ✅ bien: protegido
@app.get("/api/documents")
def list_docs(user = Depends(require_role("admin"))):
    ...

# 🔴 MAL: sin dependencia de auth → CUALQUIER usuario accede
@app.get("/api/admin-panel")
def admin_panel(user = Depends(get_current_user)):  # solo auth, NO authz
    ...
    # Esto es un bug de seguridad: el viewer NO debería estar acá,
    # y el endpoint NO lo verifica.
```

En revisión de código se busca **SIEMPRE** si algún endpoint nuevo olvidó la
dependencia de autorización. Eso es "deny-by-default": el default es que
NO puedas acceder, y solo cuando una dependencia lo permite, podés.

---

## 7 · Matriz de autorización (la que vas a implementar)

Esta tabla es tu **checklist de diseño**: la escribís ANTES de codear y cada
celda es un check del script de verificación.

| Acción | admin | editor | viewer |
|--------|:-----:|:------:|:------:|
| Ver documento público | ✅ | ✅ | ✅ |
| Ver documento privado de OTRO usuario | ✅ | ❌ 403 | ❌ 403 |
| Crear documento (draft privado) | ✅ | ✅ | ❌ 403 |
| Publicar documento | ✅ (el suyo o el de otro) | ✅ (solo el suyo) | ❌ 403 |
| Editar documento de OTRO | ✅ | ❌ 403 | ❌ 403 |
| Borrar CUALQUIER documento | ✅ | ❌ 403 | ❌ 403 |
| Gestionar usuarios (cambiar rol) | ✅ | ❌ 403 | ❌ 403 |
| Ver documentos de OTRA empresa (tenancy) | ❌ 403 | ❌ 403 | ❌ 403 |
| Crear con token read-only (scope) | ❌ 403 | ❌ 403 | ❌ 403 |

---

## 8 · Flujo de la entrega: qué hacés y qué te dan

```
TENÉS DADO (NO modificás):          VOS LO COMPLETÁS (los 3 archivos):
  · models.py (rol, tenant, doc)      · dependencies.py
  · storage.py (2 tenants, 4 users,     ├─ require_role
      5 docs)                          └─ require_scope
  · security.py (hash + JWT)          · controllers/users_controller.py
  · auth_common.py (verify login)       (3 endpoints: list, get, change_role)
  · auth_controller.py (login con      · controllers/documents_controller.py
      claims role/scope)                (6 endpoints: CRUD + publish)
  · config.py, main.py
```

El script `scripts/verificar_authz.sh` prueba **44 checks** — uno por celda
de la matriz de arriba. Los 44 checks verdes = entrega aprobada en práctica.

---

## 9 · Bibliografía y recursos

### Conceptos fundamentales
- **OWASP A01 Broken Access Control** (Top 10 2021): la referencia oficial. [owasp.org/Top10](https://owasp.org/Top10/)
- **OWASP RBAC Cheat Sheet**: patrones y anti-patrones. [cheatsheetseries.owasp.org](https://cheatsheetseries.owasp.org/cheatsheets/Role-Based_Access_Control_Cheat_Sheet.html)
- **AuthN vs AuthZ — NIST SP 800-63C**: la distinción formal.

### FastAPI y dependencias
- **FastAPI Security docs**: dependencies, OAuth2 scopes, JWT. [fastapi.tiangolo.com/tutorial/security](https://fastapi.tiangolo.com/tutorial/security/)
- **FastAPI's `Depends` pattern**: la documentación oficial de las dependencias reutilizables.

### Videos recomendados (previo a la clase)
- **Hussein Nasser**: "Authorization vs Authentication — A Crucial Distinction"
  (YouTube, ~15 min) — explica por qué mezclar AuthN con AuthZ genera bugs.
- **OWASP**: "Broken Access Control Explained" (YouTube, ~20 min) — ejemplos reales de A01.

### Textos académicos
- **NIST SP 800-162** (Guide to RBAC): el estándar de referencia para modelos de roles.
- **Introduction to RBAC** (ACM Computing Surveys): análisis formal de los tipos de RBAC.

---

## 10 · Checklist de estudio (antes de la clase)

- [ ] Puedo explicar con mis palabras la diferencia entre `401` y `403`.
- [ ] Recuerdo qué es IDOR y por qué `GET /api/posts/{id}` sin owner check es el bug A01 más común.
- [ ] Sé que RBAC asigna permisos a ROLES, no a usuarios.
- [ ] Entiendo que el scope es del TOKEN y el rol es del USUARIO (no son lo mismo).
- [ ] Sé que multi-tenancy = filtrar por `tenant_id` SIEMPRE, incluso en documentos públicos.
- [ ] Entiendo que deny-by-default significa: endpoint sin dependencia de authz = vulnerabilidad.
- [ ] Leí el mapeo OWASP del Módulo 05 (docs/OWASP.md) — este nivel lo pasa de 🔴 a 🟢.

---

> **Tiempo estimado de lectura**: 35-40 minutos.
> **Acordate**: el material es complementario y de práctica. La spec de la entrega
> está en `SPEC.md`. Leé primero este material y después seguí con la SPEC.
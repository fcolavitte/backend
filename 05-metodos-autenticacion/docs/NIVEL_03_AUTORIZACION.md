# Nivel 03 — Autorización: de "¿quién sos?" a "¿qué podés hacer?"

> **Este documento es la propuesta de clase para la próxima clase asincrónica.**
> Es el puente entre lo que ya viste (autenticación, módulo 05) y el
> siguiente salto: **autorización**.
>
> Prerequisito conceptual: haber hecho el Nivel 01 (`docs/OWASP.md`) y el
> Nivel 02 (rate limit + headers + fail-loud) del módulo 05. En particular,
> entender por qué **autenticación (A07) ≠ autorización (A01)** — esa
> distinción es el corazón de este documento.

---

## TL;DR (si solo leés 30 segundos)

- **Autenticación** responde **"¿quién sos?"** → viste los 7 métodos.
- **Autorización** responde **"¿qué podés hacer?"** → es la pieza que falta.
- La #1 del OWASP Top 10 desde 2021 es **A01 · Broken Access Control** = un
  fallo de AUTORIZACIÓN. Los 7 métodos de auth que hiciste no la cubren.
- El error más común en producción: "el usuario está logueado, listo".
  No. **Logueado ≠ autorizado** para ver/escribir/borrar X.
- Este nivel se enseña con un **proyecto práctico completo**: una API de
  documentos con roles reales, scopes, tenancy y deny-by-default.

---

## 1 · El problema (por qué existe este nivel)

Tomá la API del módulo 05: cualquier usuario autenticado (con cualquiera de
los 7 métodos) llega a `GET /api/me/...`. Eso es correcto para "quién soy",
pero es un desastre si la API tuviera `GET /api/posts/{id}` o
`DELETE /api/users/{id}`, porque:

| Pregunta                                     | ¿Lo cubre la auth? |
|----------------------------------------------|--------------------|
| ¿Es un usuario válido? (¿login OK?)          | ✅ Sí — 7 métodos  |
| ¿Puede leer el post #42?                     | ❌ No              |
| ¿Puede borrar posts de OTRA persona?         | ❌ No              |
| ¿Solo la empresa demo@corp puede ver sus docs? | ❌ No            |
| ¿Un viewer puede crear posts?                | ❌ No              |

**Ni los 7 métodos, ni el JWT, ni OAuth2 responden eso.** Un JWT solo dice
"qué te identifica" (`sub`). Decidir si HACER una acción es autorización.

> **Lección clave #1**: auth ≠ authz. El JWT prueba quién sos. La RUTA (código)
> decide si lo que pedís te corresponde. Confundirlos es la fuente de los
> incidentes de seguridad más caros de la historia reciente.

---

## 2 · Los 4 pilares de la autorización (lo que se enseña)

### Pilar 1 — RBAC (Role-Based Access Control)

Asignás roles a usuarios y permisos a roles. NUNCA permisos directos a
usuarios sueltos (se vuelve inmantenible).

```
Roles:    admin → editor → viewer
Permisos:
  admin   → crear/editar/borrar users, borrar posts, ver todo
  editor  → crear/editar posts, ver todo
  viewer  → ver solo lo publicado
```

En FastAPI eso se traduce en **dependencias** reutilizables:

```python
from fastapi import Depends, HTTPException, status

def require_role(role: str):
    def checker(current_user: User = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(status_code=403, detail="No tenés el rol necesario")
        return current_user
    return checker

# Uso:
@app.delete("/api/posts/{post_id}")
def delete_post(current_user: Annotated[User, Depends(require_role("admin"))]):
    ...
```

**El 403** (Forbidden) es el código que responde la autorización → deniega.
El 401 es de autenticación → "no sé quién sos". Mezclarlos confunde al
cliente y es señal de código que no distingue ambos niveles.

### Pilar 2 — Object-level access control (per-entity)

Es el más violado (A01) y el más fácil de pasar por alto. Un `viewer` puede
tener el rol correcto pero **no debería poder ver el post privado de otro**.

```python
# MAL: cualquier autenticado que conozca el id lo ve   <- Broken Access Control
@app.get("/api/posts/{post_id}")
def get_post(post_id: int, current_user: Annotated[User, Depends(get_current_user)]):
    return storage.get_post(post_id)

# BIEN: el dueño (o un admin) es quien puede verlo/modificarlo
@app.get("/api/posts/{post_id}")
def get_post(post_id: int, current_user: Annotated[User, Depends(get_current_user)]):
    post = storage.get_post(post_id)
    if post.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No podés ver este post")
    return post
```

Esto es **IDOR** (Insecure Direct Object Reference): "meto el id que quiero
y veo lo de otro". Es el ataque A01 más común. Mándale `GET /api/posts/1`,
`/2`, `/3`… en un sistema roto, y leés los datos de todos.

### Pilar 3 — Scopes (en OAuth2 reales)

En el módulo 05 el OAuth2 tenía un solo flujo (password) y un token sin
scopes. En producción el access token lleva **scopes** que limitan qué puede
hacer EL TOKEN (independientemente del usuario):

```
scope: "read"            → solo GET
scope: "read write"      → GET + POST/PUT/DELETE
scope: "email profile"   → puodés leer email y perfil
```

En JWT viajan como un claim `scope`/`scopes`:

```json
{
  "sub": "1",
  "scope": "read",
  "exp": 1788905287
}
```

Y el endpoint valida que el scope del TOKEN alcance para la operación:

```python
@app.get("/api/posts")
def list_posts(
    current_user: Annotated[User, Depends(require_scope("read"))],
):
    ...

@app.post("/api/posts")
def create_post(
    current_user: Annotated[User, Depends(require_scope("write"))],
):
    ...
```

Diferencia sutil pero importante: el **rol** es del usuario; el **scope** es
de ESTE token. Un token "read-only" emitido para una integración no debería
poder escribir, aunque el usuario humano sea admin.

### Pilar 4 — Multi-tenancy + deny-by-default

**Tenancy**: cada inquilino (empresa, organización) ve SOLO sus datos. La
regla se aplica en TODA query con filtro por `tenant_id`, nunca olvidándose.

```python
# SIEMPRE filtrar por el tenant del usuario autenticado
def get_my_docs(current_user: Annotated[User, Depends(get_current_user)]):
    return storage.list_docs(tenant_id=current_user.tenant_id)
    # NUNCA: return storage.list_docs()
```

**Deny-by-default**: si no hay una regla que PERMITA, el default es denegar.
Se implementa con una dependencia final que lanza 403 si nada autorizó:

```python
@app.get("/api/audit/logs")
def audit_logs(
    current_user: Annotated[User, Depends(require_role("admin"))],
):
    # Si el rol no es admin, require_role ya lanzó 403 antes de entrar acá.
    # Cualquier endpoint nuevo SIN dependencia de authz es un bug de seguridad.
```

> **Lección clave #2**: deny-by-default significa que agregar un endpoint y
> olvidarte de la dependencia de autorización = vulnerabilidad abierta. En
> la revisión de código esto se busca SIEMPRE.

---

## 3 · El ataque que este nivel mitiga (y cómo lo vemos vivo)

### La demo que se proyecta en clase: el escalamiento horizontal

Arrancamos con una API "solo con auth" (los 7 métodos). Y la atacamos:

```
1. GET /api/me → "hola demo"            (auth OK, cualquiera)
2. GET /api/documents/1 → documento privado de OTRO usuario
     → 200. LUSTRADA. Esto es Broken Access Control.
```

Después aplicamos RBAC + object-level + tenancy y repetimos:

```
1. GET /api/me → "hola demo"
2. GET /api/documents/1 → 403 (no es tu doc)
3. GET /api/documents (como viewer) → solo los publicados
4. DELETE /api/documents/1 (como viewer) → 403 (rol no alcanza)
```

El alumno VE cómo el mismo request que antes pasaba, ahora da 403 — no
porque cambió la auth, sino porque agregamos la CAPA de autorización.

### La matriz de autorización (el checklist que se revisa)

| Acción                            | admin | editor | viewer |
|-----------------------------------|:-----:|:------:|:------:|
| Ver documentos públicos           |  ✅   |   ✅   |   ✅   |
| Ver documentos privados de otro   |  ✅   |  ❌403 |  ❌403 |
| Crear documento (draft)           |  ✅   |   ✅   |  ❌403 |
| Publicar                          |  ✅   |   ✅   |  ❌403 |
| Editar doc de otro                |  ✅   |  ❌403 |  ❌403 |
| Borrar cualquier documento        |  ✅   |  ❌403 |  ❌403 |
| Gestionar usuarios (cambiar rol)  |  ✅   |  ❌403 |  ❌403 |

Una tabla así, escrita ANTES de codear, es threat modeling práctico (cierra
A04 del mapa OWASP).

---

## 4 · Plan de trabajo para la clase (proyecto práctico)

### Objetivo de la clase

Construir, en el mismo estilo del módulo 05 (FastAPI + Pydantic + test ),
una **API de documentos** con autorización completa: RBAC + object-level +
scopes + tenancy + deny-by-default. Todo verificable con un script como el
`verificar_metodos.sh`.

### Checklist de entregables

1. **Modelo de roles** en el usuario (`role: str` con enum `admin|editor|viewer`)
   y **tenant** (`tenant_id`).
2. **Dependencias** reutilizables: `require_role`, `require_scope`, y el
   filtro de tenancy para documentos.
3. **Endpoints protegidos** con las dependencias. Cada uno deniega por
   defecto (403).
4. Delete/create/update **respetan** owner + rol (IDOR mitigado).
5. **OAuth2 token con `scope`** en el claim, y `require_scope` que lo valida.
6. **Multi-tenancy**: dos empresas demo, cada una ve solo la suya.
7. **Script `verificar_authz.sh`** que comprueba cada caso de la matriz
   (200/403 esperados). Igual que el módulo 05.
8. **Documentar en `OWASP.md`**: cerrar el 🔴 de A01 con evidencia nueva.

### Test que los alumnos deben pasar (parte de la corrección)

```bash
./scripts/verificar_authz.sh   # todos los checks verdes = clase aprobada en práctica
```

Cada check es un caso de la matriz → el alumno entiende "qué caso de abuso
estoy cubriendo" en lugar de "qué método escribí".

---

## 5 · Integración con el SSO real (Keycloak/Google) — el paso final

La teoría cerrada necesita un IdP de verdad. El plan de cierre:

1. Levantar **Keycloak** (docker) o usar **Google** con flujo authorization
   code + PKCE (el flujo "real" del módulo 07, que ahí era simulado).
2. El IdP emite un access_token **con scopes y roles** de verdad.
3. Nuestra API valida contra el **JWKS** del IdP (clave pública), no contra
   nuestra SECRET_KEY. Ahí se ve el cambio: `decode_token` con clave de IdP.
4. Repetir la matriz de autorización con usuarios reales de Keycloak.

Eso cierra el ciclo: autenticación (módulo 05) → autorización (este nivel) →
identidad federada de producción (Keycloak). Es un sandbox realista sin
depender de infra externa.

---

## 6 · Resumen para estudiar antes de la clase

- [ ] Puedo explicar con mis palabras la diferencia entre 401 y 403.
- [ ] Recuerdo qué es IDOR y por qué `GET /api/posts/{id}` sin owner check
      es el bug A01 más común.
- [ ] Sé que RBAC asigna permisos a ROLES, no a usuarios.
- [ ] El scope es del TOKEN; el rol es del USUARIO. No son lo mismo.
- [ ] Multi-tenancy = filtrar por `tenant_id` SIEMPRE, nunca olvidar.
- [ ] Deny-by-default: un endpoint sin dependencia de authz es un bug.
- [ ] Releí el mapeo A01 en `OWASP.md` — este nivel lo pasa de 🔴 a 🟢.

---

## Recursos

- OWASP A01 Broken Access Control (referencia de la categoría completa).
- El tutorial de FastAPI "Security" → secciones de dependencias y OAuth2.
- El módulo 05 ya te dio la base: este nivel es la continuidad natural.
- Práctica recomendada: reproducí el panel 8 (rate limit) pero con una
  "matriz" que pruebe la autorización de cada endpoint.
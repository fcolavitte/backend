# Frontend — Laboratorio de Autorización RBAC (Módulo 06)

Panel interactivo para **probar la matriz de autorización en vivo con los 4
usuarios demo**, mirar el **payload del JWT decodificado** (lo que el token
"le dice" al server), ver el **IDOR en tiempo real** en el probador de la
matriz y ver cómo la **consola de requests** refleja el 200 vs 403 que
devuelve el server.

## Cómo arrancar

Requisito: el backend corriendo en `http://127.0.0.1:8000`:

```bash
# (en 06-autorizacion-rbac/backend/)
uv sync
uv run -m app.main
```

Luego, en esta carpeta:

```bash
pnpm install
pnpm dev
```

Abrí `http://localhost:5173`. No hace falta CORS: el front va por el proxy
de Vite (`/api` → `127.0.0.1:8000`), mismo-origen.

> **Usamos pnpm, NO npm.** El registro/CLI de npm está bloqueado en la
> facultad; pnpm es la herramienta oficial del curso para proyectos Node.
> Nunca generes `package-lock.json` (npm) en este repo. El lockfile de
> pnpm es `pnpm-lock.yaml`.

## Qué completás

En esta carpeta hay un solo archivo 🔓 a completar. El resto del frontend
viene completo (es herramienta de prueba, no es parte de la entrega, pero
te da práctica con la UI y te muestra los helpers usándolos en vivo):

| Archivo | Qué hacés |
|---------|-----------|
| `src/authz.ts` | 6 helpers de autorización (canEdit, canDelete, scopeAllowsWrite, etc.) |

La spec completa está en [`../SPEC.md`](../SPEC.md) sección 3.4.

## Qué probar

1. **Entrá con los 4 usuarios demo** (un click cada uno). Mirá el panel
   "Tu sesión": el payload del JWT decodificado te muestra los claims
   (sub, role, tenant_id, scope).

2. **Cambiá el scope** a "read" al loguear: el panel de "Tu sesión" marca
   SOLO LECTURA y el panel de Documentos NO muestra los botones de crear/
   editar/publicar (la UI te frena, no el server — esto se alinea cuando
   completás authz.ts).

3. **Probador de la matriz**: escribí el ID de un documento del seed
   (1-5) y mandá GET/PATCH/DELETE/PUBLISH. Mirá el status en la consola.
   El caso más claro: logueate como `viewer@acme.com` y pedí GET/5
   (plan secreto de Globex). Si da 200 → IDOR (backend roto). Si da 403
   → tu backend funciona.

4. **Cambiá roles** (solo admin): entrá como `admin@acme.com`, cambiá un
   usuario a otro rol. Mirá el claim del token en "Tu sesión" — quedó
   viejo, pero el server ya trata al usuario con el rol nuevo.

5. **La consola**: cada request aparece con su status. Verdes = 2xx
   (server te dejó pasar). Amarillos/rojos = 4xx (rechazado). Si un
   request que debería ser rojo aparece en verde → tu backend tiene un
   bug de access control (completá `dependencies.py`).

## Estructura

```
src/
  api.ts          # cliente HTTP completo con consola didáctica
  types.ts        # espejo de app/models.py + JwtPayload
  authz.ts        # 🔓 COMPLETÁS VOS — 6 helpers de autorización
  App.tsx         # layout: login / sesión / probador / documentos
  components/
    HealthBar.tsx     # contadores del server en vivo
    LoginPanel.tsx    # login con 1 click + scope selector + register
    SessionInfo.tsx   # payload JWT decodificado + claim legible
    ProberPanel.tsx   # probador de IDOR / matriz por id
    UsersPanel.tsx    # gestión de usuarios (admin) + cambio de rol
    DocumentsPanel.tsx# CRUD con acciones según authz.ts
    RequestLog.tsx    # consola de requests con color por status
```

## Verificación

```bash
pnpm build   # tsc --noEmit && vite build
```

> **Lección pedagógica**: ocultar un botón no es seguridad. Los helpers de
> authz.ts replican la matriz en la UI, pero la seguridad REAL vive en el
> server (dependencies.py + controllers). Si el server está roto, la UI
> "muestra que sí" pero el server (también roto) también dice que sí — el
> 200 aparece en la consola. La defensa oral de esto es excelente material.
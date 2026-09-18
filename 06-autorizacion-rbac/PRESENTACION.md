---
marp: true
theme: default
paginate: true
backgroundColor: #ffffff
color: #111827
style: |
  /* ---- Base: theme claro global (letras negras, fondo claro) ---- */
  section {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    padding: 36px 56px;
    background-color: #ffffff;
    color: #111827;
  }
  h1 { color: #111827; font-size: 1.55em; }
  h2 { color: #1f2937; font-size: 1.25em; }
  h3 { color: #374151; font-size: 1em; }
  h4 { color: #1d4ed8; }
  strong { color: #111827; }
  em { color: #374151; }
  a { color: #1d4ed8; }

  /* ---- Slides densas: reducimos todo un escalón ---- */
  section.smaller { font-size: 0.92em; }
  section.smaller h1 { font-size: 1.4em; }
  section.smaller h2 { font-size: 1.15em; }

  /* ---- Slides de repaso (3-5) y la matriz (8): texto más grande ---- */
  section.bigger { font-size: 1.35em; }
  section.bigger h1 { font-size: 2em; }
  section.bigger h2 { font-size: 1.7em; }
  section.bigger table { font-size: 0.85em; }

  /* ---- Código ---- */
  code {
    color: #be185d;
    background: #f1f5f9;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.85em;
  }
  pre {
    background: #f8fafc;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 0.82em;
    line-height: 1.35;
    color: #383a42;
  }
  pre code {
    background: none;
    padding: 0;
    color: #383a42;
  }

  /* ---- Resaltado sintáctico (paleta One Light) ---- */
  pre code :is(.hljs-keyword, .hljs-doctag, .hljs-template-tag, .hljs-template-variable, .hljs-variable.language_, .hljs-selector-tag) { color: #a626a4 !important; }
  pre code :is(.hljs-string, .hljs-regexp, .hljs-meta .hljs-string) { color: #50a14f !important; }
  pre code :is(.hljs-title, .hljs-title.function_, .hljs-title.class_, .hljs-name, .hljs-quote, .hljs-selector-pseudo) { color: #4078f2 !important; }
  pre code :is(.hljs-attr, .hljs-attribute, .hljs-literal, .hljs-meta, .hljs-selector-attr, .hljs-selector-class, .hljs-selector-id, .hljs-variable) { color: #986801 !important; }
  pre code :is(.hljs-number, .hljs-symbol) { color: #986801 !important; }
  pre code :is(.hljs-operator, .hljs-params, .hljs-subst, .hljs-type) { color: #383a42 !important; }
  pre code :is(.hljs-comment, .hljs-code, .hljs-formula) { color: #a0a1a7 !important; font-style: italic; }
  pre code :is(.hljs-section, .hljs-bullet) { color: #e45649 !important; font-weight: 700; }
  pre code .hljs-built_in { color: #c18401 !important; }

  /* ---- Tablas ---- */
  table {
    font-size: 0.8em;
    background: #ffffff;
    border-radius: 8px;
    overflow: hidden;
    border-collapse: collapse;
    width: 100%;
  }
  thead { background: #f3f4f6; }
  th {
    color: #111827;
    padding: 5px 10px;
    text-align: left;
    border-bottom: 2px solid #2563eb;
    background: #f3f4f6;
  }
  td {
    color: #1f2937;
    padding: 5px 10px;
    border-bottom: 1px solid #e5e7eb;
    background: #ffffff;
  }
  tr:hover td { background: #f8fafc; }

  /* ---- Blockquote ---- */
  blockquote {
    border-left: 4px solid #2563eb;
    background: #f8fafc;
    padding: 8px 14px;
    border-radius: 0 8px 8px 0;
    margin: 8px 0;
  }
  blockquote p {
    color: #475569;
    font-style: italic;
  }

  /* ---- Listas ---- */
  ul { list-style-type: none; padding-left: 0; }
  ul li::before { content: "▸ "; color: #1d4ed8; font-weight: bold; }
  ul li { color: #1f2937; line-height: 1.5; }
  ol li { color: #1f2937; line-height: 1.5; }

  /* ---- Lead slides ---- */
  section.lead h1 { font-size: 2.2em; }
  section.lead p { color: #374151; }

  /* ---- Fase ---- */
  section.fase {
    background-color: #eef2ff;
  }
  section.fase h1 { color: #4338ca; font-size: 1.7em; }
  section.fase h2 { color: #3730a3; }

  /* ---- Brecha (la lección central) ---- */
  section.brecha {
    background-color: #fef2f2;
  }
  section.brecha h1 { color: #b91c1c; font-size: 1.7em; }
  section.brecha h2 { color: #991b1b; }
  section.brecha li, section.brecha p { color: #7f1d1d; }

  /* ---- Entrega (la parte de evaluación) ---- */
  section.entrega {
    background-color: #f0fdf4;
  }
  section.entrega h1 { color: #15803d; font-size: 1.7em; }
  section.entrega p, section.entrega li { color: #14532d; }

  /* ---- Bibliografía ---- */
  section.biblio {
    background-color: #eff6ff;
  }
  section.biblio h1 { color: #1d4ed8; font-size: 1.6em; }
  section.biblio h2 { color: #4338ca; font-size: 1.05em; }
  section.biblio li { font-size: 0.82em; line-height: 1.45; color: #1f2937; }

  /* ---- Footer ---- */
  footer { color: #64748b; font-size: 0.6em; }
---

<!-- _class: lead -->
<!-- note: |
  MINUTO 0-1 · BIENVENIDA
  Frase de apertura: "Hoy cerramos la trilogía de la seguridad: el 04 le puso
  identidad a la API (autenticación), el 05 les dio los vehículos (sesión y
  token), y HOY la API aprende a decidir qué PODÉS hacer (autorización)".
  Aviso temprano y sin vueltas: hay ENTREGA OBLIGATORIA el 22/09 — va a
  aparecer varias veces en la clase, no es un rumor.
  Animar a los que no hicieron la lectura previa: todavía hay tiempo, el
  MATERIAL_PREVIO.md es la base y la actividad de hoy los pone al día.
  Si alguien pregunta "¿qué hacemos hoy?", responder con la frase de la
  portada: "en el 04 la API aprendió quién sos; hoy aprende qué podés hacer".
-->

# Autorización RBAC

### Clase 06 — Desarrollo de Software 2026 · 🚦 ENTREGA OBLIGATORIA

En el 04 la API aprendió **quién sos**. Hoy la API aprende **qué podés hacer**.

---

<!-- note: |
  MINUTO 1-2 · LA AGENDA
  Recorrer la tabla rápido, sin leerla: cada fila es una promesa de la clase.
  1) Repaso 04-05 (5 min): "para que arranquemos todos desde el mismo lugar".
  2) La brecha A01 (3 min): "la lección más importante del curso, un solo
     concepto que hoy van a aplicar 44 veces".
  3) El módulo 06 (4 min): "el mapa de los 5 pilares, no los van a leer acá,
     la spec los espera".
  4) Actividad (60 min): "aula invertida: la teoría se leyó en casa, hoy se
     construye SOLO y se entrega".
  5) Entrega: "la fecha no se corre: 22/09 23:59, y la defensa oral es 30%.
     Repito: no se corre".
  Cerrar con el blockquote: si no hicieron la lectura previa, "la clase les
  va a pasar por la ventana" — con tono de advertencia amable, no de amenaza.
-->

## La clase de hoy

| # | Momento | Qué pasa |
|---|---------|----------|
| 1 | **Repaso 04-05** (5 min) | AuthN: identidad, JWT, los 7 vehículos |
| 2 | **La brecha A01** (3 min) | Estás logueado ≠ podés hacerlo. OWASP lo confirma |
| 3 | **El módulo 06** (4 min) | RBAC + object-level + scopes + tenancy + la matriz |
| 4 | **Docker Compose** (1 min) | 🐳 Portabilidad: el entorno entero, un solo comando |
| 5 | **Actividad** (60 min) | Leé la SPEC y completá los 4 archivos 🔓 |
| 6 | **Entrega obligatoria** | Rollo: fork + PR antes del **22/09 23:59** |

> La lectura previa (`MATERIAL_PREVIO.md`) ya la hiciste en casa. Si no, hoy
> vas a ver pasar la clase por la ventana y la fecha límite no se corre.

---

<!-- _class: bigger -->
<!-- note: |
  MINUTO 2-4 · REPASO CLASE 04 — 4 HITOS, 30 SEG CADA UNO
  Contexto: "En el 04 la API pasó de recibir cualquier request a saber quién
  sos — eso es AUTENTICACIÓN, y este módulo NUNCA vuelve a tocar eso".
  1) Argon2: preguntar en voz alta "¿quién se acuerda qué hash usamos?" →
     Argon2 vía pwdlib. Explicar en una frase por qué lento: "lento para el
     atacante que quiere romperlo 1000 veces, y para nosotros pasa
     desapercibido porque lo corremos una vez por login".
  2) JWT firmado: preguntar "¿el JWT se firma o se encripta?" → SE FIRMA, y
     por eso el payload es LEGIBLE sin el secreto. Mostrar el ejemplo del
     JSON: "cualquiera puede decodificar sub/iat/exp, lo que la firma protege
     es que nadie los altere". Esto es lo que más se confunde en la materia.
  3) Sesión vs JWT: el tradeoff — "sesión: el estado vive en el server, lo
     revocás al instante; JWT: stateless, no hay nada que revocar, escala".
  4) OWASP: nombrar que la autenticación débil entra en el Top 10 (A07 en la
     edición 2021), y ahí está el gancho: "y el puesto 1 es de OTRO bug, que
     es justo el de la clase de hoy".
  Cierre: "El 04 dijo textual: la autorización es el próximo módulo. Hoy es
  ESE módulo. Autenticar NO es lo mismo que autorizar: la diferencia es la
  clase entera".
-->

## Repaso · Clase 04 — Autenticación

En el Módulo 04 la API pasó de recibir **cualquier request** a saber **quién sos**:

1. **Hash Argon2** — la contraseña NUNCA se guarda en texto plano.
   Guardamos un hash *irreversible y lento*. (¿Alguno se acuerda de pwdlib?)

2. **JWT firmado** — al loguear, el server emite un token **firmado**:
   `header.payload.firma`. Ojo: se **firma**, no se encripta →
   el payload es legible sin el secreto.

```python
# security.py (04/05/06) — el payload del JWT es legible SIN el secreto
{"sub": "1", "iat": 1717..., "exp": 1718...}
```

3. **Sesión server-side vs JWT** — estado en el server (revocación
   inmediata) vs token autocontenido (stateless, escala).

4. **OWASP** — las amenazas de la autenticación (A07/A02 de aquel momento).

> La lección del 04: *"sin saber quién sos, no podés decidir qué podés hacer"*
> — y esa última parte es EXACTAMENTE la clase de hoy.

---

<!-- _class: bigger -->
<!-- note: |
  MINUTO 4-6 · REPASO CLASE 05 — LA TABLA DE LOS 7 VEHÍCULOS
  Avisar: "el 05 fue asincrónico, así que repasamos lo esencial: los 7
  métodos responden TODOS a la misma pregunta: ¿cómo demuestro quién soy?".
  Recorrer la tabla por filas, 15-20 seg cada una, sin leer — la lección:
  1) Basic: "base64 NO es cifrado, es codificación — solo HTTPS lo salva".
  2) Session: "la cookie httpOnly con estado en el server: la revocás al
     instante. Es la arquitectura que usa la facultad".
  3) Token opaco: "la misma idea pero sin cookie: pensado para APIs".
  4) JWT header: "stateless: no hay estado que revocar; el token vive solo".
  5) JWT cookie: "el mismo token pero en cookie httpOnly: cambia el juego
     XSS vs CSRF según el vehículo que elijas".
  6) OAuth2: "el PROTOCOLO — OAuth2 define el flujo; JWT es el FORMATO del
     token que viaja por ese flujo. No son lo mismo, es la pregunta trampa".
  7) SSO: "el IdP emite el id_token y vos validás iss/aud: SSO es la
     experiencia; OAuth2/OIDC es el protocolo que la hace posible".
  Rate limit: "6 intentos fallidos → 429 Retry-After: la seguridad también
  es política".
  CIERRE CLAVE — hacer pausa antes del blockquote: "Todos resuelven cómo
  demostrar quién sos. ¿Y qué podés hacer cuando lo demostraste? NINGUNO
  responde eso". Ese hueco se llama AUTORIZACIÓN — "y es exactamente la
  clase de hoy".
-->

## Repaso · Clase 05 — Los 7 vehículos de identidad

| Método | Cómo demuestra quién sos | La lección |
|--------|--------------------------|------------|
| **1 · Basic** | `Authorization: Basic base64(usuario:pass)` | base64 ≠ cifrado. Solo sobre HTTPS |
| **2 · Session** | cookie `session_id` httpOnly, estado en server | revocación inmediata · es la cookie de la facultad |
| **3 · Token opaco** | `Bearer <token aleatorio>` guardado en server | igual que session, sin cookie → para APIs |
| **4 · JWT header** | `Bearer <jwt firmado>` | **stateless**: no hay estado que revocar |
| **5 · JWT cookie** | el mismo JWT, pero en cookie httpOnly | tradeoff XSS vs CSRF según el vehículo |
| **6 · OAuth2** | `POST /token` (grant_type=password) | OAuth2 es el PROTOCOLO; JWT es el FORMATO |
| **7 · SSO** | el IdP emite id_token validado (iss/aud) | SSO es la experiencia; JIT provisioning |

Y la frutilla: **rate limit** — 6 intentos fallidos → `429 Retry-After`.

> Todos resuelven la MISMA pregunta: **"¿cómo demuestro quién soy?"**
> Ninguno responde **"¿qué puedo hacer?"**. Ese hueco se llama AUTORIZACIÓN.

---

<!-- _class: bigger -->
<!-- note: |
  MINUTO 6-8 · LAS 3 PREGUNTAS — LA PROMESA CUMPLIDA
  Esta es la slide que conecta TODO el recorrido del curso: traer la tabla
  del módulo 04 (ya la vieron) y decir: "el 04 nos dejó esta tabla y una
  promesa: la autorización era el próximo módulo. Bien: hoy es ese módulo".
  Fila por fila:
  1) ¿Quién sos? → Autenticación → "resuelto en 04 y 05, no lo tocamos más".
  2) ¿Qué podés hacer? → Autorización → "HOY. Y ojo: es la única pregunta que
     la industria responde peor — el 1º del Top 10 de OWASP".
  3) ¿Cómo lo demuestro? → Sesión/Token → "resuelto: son los vehículos del 05".
  Leer la cita del módulo 04 EN VOZ ALTA: "la autorización es el próximo
  módulo" — genera el momento de reconocimiento en el aula.
  Cierre: "hoy termina la trilogía. Con la autorización, la API tiene las
  tres patas: identidad, vehículo y permiso".
  Si alguien pregunta por el "aula invertida" de la segunda fila: explicar
  que RBAC (Role-Based Access Control) es el modelo de la clase y que la
  teoría se leyó en casa — acá se implementa en vivo.
-->

## Las 3 preguntas (la promesa del Módulo 04)

En el 04 vimos esta tabla y quedó una promesa pendiente:

| Pregunta | Nombre | Estado |
|----------|--------|--------|
| 1 · ¿Quién sos? | **Autenticación** | ✅ Clases 04 y 05 |
| 2 · ¿Qué podés hacer? | **Autorización** | ⬅️ **HOY** (aula invertida) |
| 3 · ¿Cómo lo demuestro? | Sesión / Token | ✅ Clases 04 y 05 |

> *"La autorización es el próximo módulo"* — lo dijo la clase 04.
> **Hoy es ese próximo módulo.** Y termina la trilogía de la seguridad.

---

<!-- _class: brecha -->
<!-- note: |
  MINUTO 8-9 · LA BRECHA #1 — OWASP A01 (LA MÁS IMPORTANTE DE LA CLASE)
  Bajar el ritmo: esta slide es la razón de ser del módulo entero.
  Decir: "desde 2021 el puesto 1 del Top 10 de OWASP NO es la inyección:
  es Broken Access Control — la autorización rota. La vulnerabilidad más
  común del mundo es justo la que hoy van a arreglar".
  Leer la pesadilla DESPACIO, línea por línea, en voz alta:
  "Sos viewer de Acme. Pedís GET /api/documents/5 — el plan secreto de
  Globex. Tu rol no debería poder. Pero NADA en el server lo verifica.
  Respuesta: 200 OK" — hacer una pausa en el "200 OK", es el punchline.
  Explicar el mecanismo en 2 frases: "el endpoint existe, el documento
  existe, y el server autenticó (sabe quién sos) pero NUNCA preguntó si
  un viewer puede pedir ese documento. Falta la capa de AUTORIZACIÓN".
  Introducir el acrónimo IDOR (Insecure Direct Object Reference): "así se
  llama este bug cuando hablás con URLs directas, y es el bug del módulo".
  MOSTRAR EN VIVO (opcional si el tiempo da): abrir el frontend del módulo
  06, loguearse como viewer@acme.com, pedir el documento 5 y mostrar el
  200 — "esto es lo que hoy vamos a eliminar".
  Cierre con el blockquote: "autenticar ≠ autorizar. Son las dos caras de
  la misma puerta: sin la segunda, la primera no alcanza".
  REGLA DEL ORADOR: no señalar a nadie que no leyó; esta es la pregunta de
  la clase, no una humillación.
-->

## La brecha #1 de la industria (OWASP A01)

Desde 2021, el **Top 10 de OWASP** pone en primer lugar:

> **Broken Access Control** — "la autorización rota" supera a la inyección.

La pesadilla en una línea:

```
Sos viewer de Acme. Pedís GET /api/documents/5 (plan secreto de Globex).
Tu rol no debería poder. Pero NADA en el server lo verifica.
Respuesta: 200 OK. 🕳️
```

Ese caso (conocido como **IDOR**) es EXACTAMENTE el que vas a arreglar hoy:
el endpoint existe, el documento existe, y el server **no pregunta quién pide**.

> La autenticación de las clases 04-05 ya te dijo *quién sos*.
> La autorización de hoy decide si ese *quién* tiene **permiso**. Son las
> dos caras de la puerta: sin la 2ª, la 1ª no alcanza.

---

<!-- note: |
  MINUTO 9-10 · LOS 5 PILARES — EL MAPA CONCEPTUAL DEL MÓDULO
  Introducción: "esto NO es teoría para memorizar: es el mapa de lo que van
  a implementar en 60 minutos. Cinco pilares, 20 segundos cada uno".
  1) RBAC: "rol = conjunto de permisos. admin/editor/viewer. Un viewer que
     borra un documento recibe 403".
  2) Object-level: "el permiso depende del OBJETO: un editor ve sus
     documentos pero NO el privado de otro editor. Acá se mitiga el IDOR
     de la slide anterior, en GET /documents/{id}".
  3) Scopes: "el TOKEN tiene límites propios, distintos del rol: un admin
     con scope read NO puede crear documentos. Rol y scope se cruzan".
  4) Multi-tenancy: "cada empresa ve SOLO lo suyo: el admin de Globex no ve
     los usuarios de Acme, aunque su rol sea admin".
  5) Deny-by-default: "regla de oro: si un endpoint no tiene autorización,
     es un bug. No lo duden, no lo negocien: cualquier endpoint sin
     verificación es una puerta abierta".
  Cierre: "todo eso lo resume LA MATRIZ — que es la próxima slide. Y esa
  matriz la mide un script con 44 checks: no hay opiniones, hay hechos".
-->

<!-- _class: fase -->

## El módulo 06 — los 5 pilares

| Pilar | Qué resuelve | El caso que vas a probar |
|-------|--------------|--------------------------|
| **RBAC** | Roles `admin`·`editor`·`viewer` con permisos | viewer recibe 403 al borrar |
| **Object-level** | Un editor no ve el privado de otro | **IDOR mitigado** en `GET /documents/{id}` |
| **Scopes** | El TOKEN tiene límites propios | admin con scope `read` no crea documentos |
| **Multi-tenancy** | Cada empresa ve SOLO la suya | admin de Globex no ve usuarios de Acme |
| **Deny-by-default** | Endpoint sin autorización = bug | cualquier endpoint sin `Depends` es una puerta abierta |

> **La matriz de autorización**: cada celda define qué HTTP code devuelve
> cada rol. El script `verificar_authz.sh` (44 checks) la mide por vos.

---

<!-- note: |
  MINUTO 10-11 · LA MATRIZ — EL CORAZÓN DE LA ENTREGA
  Presentarla como "la tabla de verdad del módulo: aparece en la SPEC, en el
  frontend y en la defensa oral. Si la entendés, la entrega es trivial".
  Recorrer SOLO las celdas clave (no leer todas):
  - "Listar usuarios / cambiar roles": solo admin. Los otros dos → 403.
  - "Crear/editar/publicar": admin todo, editor lo suyo, viewer 403.
  - FILA CLAVE: "Ver doc privado de OTRO": admin ✅ (puede todo), editor y
    viewer → 403. PARAR acá: "esa fila es el IDOR arreglado: el server
    ahora compara quién pide vs quién es dueño".
  - "Otra empresa": TODOS 403, incluso admin: el tenant es parte de la
    identidad, ningún rol lo salta.
  - "Escribir con token read": TODOS 403: el scope limita al rol.
  Cierre: "las celdas en rojo son exactamente las que el script verifica,
  una por una. La consigna es una sola: que el server devuelva tal cual".
  NO explicar cómo implementar cada celda: eso es la actividad. Esta slide
  es el CONTRATO, no la solución.
-->

<!-- _class: bigger -->

## La matriz (el corazón de la entrega)

| Operación | admin | editor | viewer |
|-----------|:-----:|:------:|:------:|
| Listar usuarios / cambiar roles | ✅ | 403 | 403 |
| Crear / editar / publicar documentos | ✅ | ✅ lo suyo | 403 (scope read) |
| **Ver doc privado de OTRO** | ✅ | **403** | **403** |
| Ver doc de otra empresa | 403 | 403 | 403 |
| Borrar documentos | ✅ | 403 | 403 |
| Escribir con token `read` | 403 | 403 | 403 |

> Las celdas en **rojo son las que el script verifica**: 44 casos de esta
> matriz, uno por uno. Tu trabajo es que el server las devuelva tal cual.

---

<!-- note: |
  MINUTO 11-12 · EL PLAN — AULA INVERTIDA + ENTREGA INDIVIDUAL
  Aviso clave: "hoy es DISTINTO al resto del curso: no hay grupos. Es
  individual, con entrega, y la dinámica es aula invertida: la teoría se
  leyó en casa, acá se construye".
  Recorrer la tabla de minutos:
  - 0-5: "léanla SPEC PRIMERO. La spec define los 4 archivos y citas la
    matriz: no se codea sin spec".
  - 5-30: backend en orden — dependencies.py (las dependencias con
    require_role), users_controller.py, documents_controller.py.
  - 30-40: script — "bash scripts/verificar_authz.sh, tienen que ver 44/44
    verdes. El script es el juez".
  - 40-55: frontend — "authz.ts: alineen la UI con el server: si el server
    devuelve 403, la UI no puede mostrar la acción".
  - 55-60: "preparen la entrega: fork + PR + copia de la salida del script".
  COMANDOS: leerlos y aclarar — "la API corre en :8000, el frontend en
  :5173, DOS terminales. El backend se levanta con uv, el frontend con
  pnpm (igual que el módulo 04)".
  REGLA DEL TALLER — leerla textual: "el docente no da respuestas, hace
  preguntas. Si te trabás, escuchás: '¿qué debería devolver el server si vos
  fueras viewer?' — esa pregunta destraba casi todo".
-->

<!-- _class: fase -->

## El plan — aula invertida + entrega individual

> La lectura ya la hiciste en casa. Hoy construís **SOLO**.

| Min | Qué hacés |
|-----|-----------|
| 0-5 | **Leé la SPEC** (`SPEC.md`) — la spec de la entrega manda |
| 5-30 | **Backend**: `dependencies.py` → `users_controller.py` → `documents_controller.py` |
| 30-40 | **Verificá**: `bash scripts/verificar_authz.sh` (mete 44/44 verdes) |
| 40-55 | **Frontend**: completá `authz.ts` y alineá la UI con el server |
| 55-60 | **Prepará la entrega**: fork + PR + copiá la salida del script |

```bash
cd 06-autorizacion-rbac/backend && uv sync && uv run -m app.main   # :8000
cd ../frontend && pnpm install && pnpm dev                          # :5173
```

> **Regla del taller**: el docente no da respuestas. Hace preguntas.
> *"¿Qué debería devolver el server si vos fueras viewer?"* destraba casi todo.

---

<!-- _class: fase -->
<!-- note: |
  MINUTO 12-13 · DOCKER COMPOSE — PORTABILIDAD (la slide más corta del curso)
  Contexto en 2 frases: "hasta acá todo se levantaba con uv y pnpm — dos
  terminales, dos instalaciones, dependencias de tu máquina. Eso tiene un
  problema: 'en mi máquina funciona'. Esta entrega mata esa frase".
  CONCEPTOS (30 segundos, uno por uno, con analogía):
  1) IMAGEN: "la receta del contenedor: el Dockerfile dice qué lenguaje, qué
     dependencias, qué comando arranca". Analogy: un plano de construcción.
  2) CONTENEDOR: "la imagen CORRIENDO: un proceso aislado que no ensucia tu
     máquina ni depende de lo que tengas instalado". Analogy: el departamento
     terminado según el plano — igual en cualquier edificio.
  3) COMPOSE: "el orquestador: un solo YAML que declara TODOS los servicios
     (postgres + backend + frontend), sus puertos, sus relaciones y un
     comando lo levanta todo". Analogy: el contratista general.
  IMPLEMENTACIÓN (40 segundos):
  - El repo ya trae docker-compose.yml + los 2 Dockerfiles → NO se modifican
    en la entrega (son infra de la cátedra, como storage.py y db.py).
  - "Un comando: docker compose up --build. Postgres en :5432 con un volumen
    (pgdata — la PERSISTENCIA: los usuarios y roles viven en la base y
    sobreviven a reinicios). Backend en :8000, frontend en :5173. El
    healthcheck del compose espera a que postgres esté sano antes de
    levantar el backend, y al backend antes de levantar el frontend".
  - "El script de verificación corre IGUAL, desde el host, contra :8000 —
    el puerto del contenedor es el mismo puerto de siempre".
  POR QUÉ (15 segundos, con la slide del blockquote): "portabilidad = el
  entorno es parte del entregable. Declarado en un YAML versionable: corre
  en el aula, en tu casa, en CI. La cátedra va a levantar TU fork con docker
  compose — si no levanta, la entrega no arranca".
  Si algún alumno no tiene Docker instalado: avisar que el flujo local uv/pnpm
  sigue disponible para DESARROLLAR, pero la validación de la entrega es sobre
  docker. Los contenedores usan la MISMA toolchain que el dev local (uv en el
  backend, pnpm vía corepack en el frontend) — cero fricción, mismo lockfile.
-->

## Docker Compose — 🐳 el entorno, portátil

**Conceptos (30 seg)**:

| Concepto | Qué es |
|----------|--------|
| **Imagen** | la receta (`Dockerfile`): lenguaje, dependencias, comando de arranque |
| **Contenedor** | la imagen CORRIENDO: proceso aislado, independiente de tu máquina |
| **Compose** | el orquestador: un YAML declara TODOS los servicios y un comando los levanta |

**Implementación (40 seg) — ya está en el repo, no se modifica**:

```bash
docker compose up --build
# postgres → localhost:5432  ·  volumen pgdata (persistencia)
# backend  → http://localhost:8000   ·   healthcheck en /api/health
# frontend → http://localhost:5173   ·   proxy /api → backend:8000
```

Y el script de verificación corre **igual que siempre**, desde el host:

```bash
bash scripts/verificar_authz.sh   # → 44 checks sobre localhost:8000
```

> **Portabilidad = el entorno es parte del entregable.** "En mi máquina
> funciona" muere hoy: la cátedra levanta TU fork con docker compose.

---

<!-- _class: entrega -->
<!-- note: |
  MINUTO 13-14 · LA ENTREGA — LEER LOS NÚMEROS EN VOZ ALTA Y DESPACIO
  Cambio de tono: esto define la nota de la materia en la parte de seguridad.
  QUÉ: "fork del repo de la cátedra + PR con los 4 archivos 🔓:
  dependencies.py, users_controller.py, documents_controller.py y authz.ts
  del frontend. El resto del repo NO se toca".
  CUÁNDO: "martes 22/09 23:59 — no se recibe por ningún otro canal: ni
  mail, ni classroom, ni pendrive. Si el PR llega a las 23:59 con network
  timeout, es problema de cómo planificaron, no de la cátedra".
  CÓMO SE CORRIGE: "el script verificar_authz.sh (44 checks) + revisión de
  código + defensa oral de 5 minutos en la clase siguiente (24/09)".
  NOTA — leer la fórmula completa: "script 40% · código 30% · defensa oral
  30%. La defensa NO es optativa: si no la hacés, perdés 30 puntos".
  TRANSPARENCIA TOTAL sobre la solución: "la solución se publica en la rama
  solucion del repo base DESPUÉS de la fecha, como en el módulo 04. Está
  bien usarla para estudiar después; copiarla ANTES no te sirve: la defensa
  oral te va a exponer en 30 segundos".
  Pregunta retórica de cierre: "¿cuántos faltan acá que van a dejar la entrega
  para el 21 a las 23? — hacé que la respuesta sea 'ninguno'".
-->

## 🚦 La entrega — obligatoria

- **Qué**: fork del repo de la cátedra + PR con los **4 archivos 🔓**
  (`dependencies.py`, `users_controller.py`, `documents_controller.py`, `authz.ts`)
- **Cuándo**: antes del **martes 22/09 23:59** — no se recibe por otro canal
- **Cómo se corrige**: script `verificar_authz.sh` (**44 checks**) + revisión
  de código + **defensa oral de 5 min** en la clase siguiente
- **Nota**: script 40% · código 30% · defensa oral 30%

> La solución se publica en la rama `solucion` del repo base **después** de la
> entrega. Copiarla sin entender solo te deja con un script que pasa y una
> defensa oral que no vas a poder sostener ni un minuto.

---

<!-- _class: biblio -->
<!-- note: |
  MINUTO 14-15 · LECTURAS SUGERIDAS (SI SOBRA TIEMPO DE LA APERTURA;
  SI NO, QUEDA COMO TAREA PARA CASA)
  Aclarar primero: "ninguna de estas lecturas es obligatoria para la entrega.
  Son las que separan un 6 de un 10 en la defensa oral".
  NIVEL 1 — OFICIAL (leer al menos una, 30 minutos):
  - OWASP A01: la fuente primaria de la brecha de hoy.
  - Authorization Cheat Sheet: cómo se hace bien en producción.
  - API Security Top 10 / BOLA: el IDOR en el mundo de las APIs — directo
    a la defensa oral.
  NIVEL 2 — TEORÍA (para el que quiere entender el porqué):
  - INCITS 359-2012: la definición formal de RBAC (roles y permisos).
  - RFC 6749 §3.3: de dónde sale el scope del token — "cuando lean la
    SPEC y vean el scope read, es esto: no lo inventamos nosotros, es RFC".
  - Multi-tenancy: por qué el tenant es parte de la identidad.
  NIVEL 3 — PRÁCTICA (las que más se aprenden):
  - Write-ups de IDOR en HackerOne: el tipo de bug que hoy aprenden a
    cerrar es de los más buscados y mejor pagados del bug bounty.
  - MATERIAL_PREVIO.md del módulo: tiene su propia bibliografía comentada —
    si no sabés por dónde arrancar, arrancá por ahí.
  CIERRE: "en la defensa oral, citar la fuente de cada decisión (OWASP, NIST,
  RFC) es la diferencia entre 'seguí la guía' y 'entendí la materia'".
-->

## Lecturas sugeridas para profundizar

**Oficial (leé al menos una)**

- OWASP Top 10 · A01 *Broken Access Control* — owasp.org/Top10/A01_2021-Broken_Access_Control/
- OWASP *Authorization Cheat Sheet* — cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- OWASP API Security Top 10 2023 · BOLA (el IDOR en APIs) — owasp.org/API-Security/

**Teoría (para la defensa oral)**

- **RBAC**: NIST/INCITS 359-2012 — la definición formal de roles y permisos
- **Scopes**: RFC 6749 (OAuth 2.0), §3.3 *Access Token Scope* — de dónde sale el `scope` del token
- **Tenancy**: *multi-tenancy authorization patterns* — por qué el tenant es parte de la identidad

**Práctica (las que más se aprenden)**

- Write-ups de **IDOR** en bug bounty (HackerOne) — el tipo de bug que hoy aprendés a cerrar
- El `MATERIAL_PREVIO.md` del módulo — con su propia bibliografía comentada

> En la defensa oral, citar de dónde sale cada decisión (OWASP, NIST, RFC)
> es la diferencia entre "seguí la guía" y "entendí la materia".

---

<!-- _class: lead -->
<!-- note: |
  MINUTO 15-16 · CIERRE DE LA APERTURA → ¡A TRABAJAR!
  Leer la frase final con la slide:
  "Hoy la API decide. Quién sos ya lo sabe (04-05). Qué podés hacer lo
  construís vos".
  Último mensaje, con el blockquote: "la Universidad te da el mapa (spec,
  matriz, script); el recorrido lo hacés vos (los 4 archivos) — y este
  recorrido tiene fecha: 22/09".
  TRANSICIÓN A LA ACTIVIDAD: "abra la SPEC, levante el backend con uv y el
  frontend con pnpm (dos terminales), y arranque. El docente da vueltas
  por el aula respondiendo preguntas CON preguntas. 60 minutos. Éxitos".
  Nota interna: durante la actividad, priorizar a los que no hicieron la
  lectura previa: se los nota trabados en la SPEC. La pregunta que más
  destraba a todos: "¿qué debería devolver el server si vos fueras viewer?".
-->

## Hoy la API decide

### Quién sos ya lo sabe (04-05). **Qué podés hacer** lo construís vos.

> *"La Universidad te da el mapa. El recorrido lo hacés vos."*
> — y este recorrido tiene fecha: **22/09**.
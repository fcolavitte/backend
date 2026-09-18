#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────
# Verificador de la MATRIZ DE AUTORIZACIÓN — Módulo 06 (RBAC)
#
# Uso: el server debe estar levantado (uv run -m app.main en backend/).
#      Con postgres: docker compose up -d postgres (o la DB que apunte
#      tu DATABASE_URL). Luego: bash scripts/verificar_authz.sh
#
# Cada check es UN CASO DE LA MATRIZ de la spec: si un check falla, sabés
# EXACTAMENTE qué caso de abuso dejaste abierto (200 donde la matriz pide 403).
#
# El script es RE-EJECUTABLE: los documentos y usuarios que crea usan ids y
# emails únicos por corrida. Los documentos seed (1..5) solo se leen.
# Con la DB PERSISTENTE las corridas se ACUMULAN, por eso los counts del
# seed se chequean como >= (mínimos), no como valores exactos.
# ──────────────────────────────────────────────────────────────────────────

set -u

BASE="${BASE:-http://127.0.0.1:8000}"
PASS="demo12345"

EMAIL_ADMIN="admin@acme.com"
EMAIL_EDITOR="editor@acme.com"
EMAIL_VIEWER="viewer@acme.com"
EMAIL_GLOBEX="admin@globex.com"

PASS_OK=0
PASS_TOTAL=0

check() {
  # check <esperado> <actual> <descripcion>
  PASS_TOTAL=$((PASS_TOTAL + 1))
  if [ "$2" = "$1" ]; then
    PASS_OK=$((PASS_OK + 1))
    echo "  ✅ $3"
  else
    echo "  ❌ $3  (esperado $1, recibido $2)"
  fi
}

check_ge() {
  # check_ge <actual> <esperado> <descripcion> — conteos con DB persistente
  PASS_TOTAL=$((PASS_TOTAL + 1))
  if [ "$1" -ge "$2" ]; then
    PASS_OK=$((PASS_OK + 1))
    echo "  ✅ $3"
  else
    echo "  ❌ $3  (esperado >= $2, recibido $1)"
  fi
}

status() { curl -s -o /dev/null -w "%{http_code}" "$@"; }

login() {
  # login <email> [scope] → access_token
  local body="{\"email\":\"$1\",\"password\":\"$PASS\""
  [ $# -ge 2 ] && body="$body,\"scope\":\"$2\""
  body="$body}"
  curl -s -X POST "$BASE/api/auth/login" -H "Content-Type: application/json" -d "$body" \
    | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4
}

json_id() {
  # json_id <respuesta-json> → el primer "id" numérico
  echo "$1" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2
}

echo ""
echo "════ MÓDULO 06 — VERIFICACIÓN DE LA MATRIZ DE AUTORIZACIÓN ════"
echo "Base: $BASE   |   Password demo: $PASS"
echo ""

# ── 0 · Health + logins de los 4 usuarios demo ────────────────────────────
echo "── 0 · Health y setup ──"
H=$(curl -s "$BASE/api/health")
check "1" "$(echo "$H" | grep -c 'Funciona')" "health responde Funciona"
check_ge "$(echo "$H" | grep -o '"users_count":[0-9]*' | cut -d: -f2)" 4 ">= 4 usuarios (4 demo del seed + re-ejecuciones)"
check_ge "$(echo "$H" | grep -o '"documents_count":[0-9]*' | cut -d: -f2)" 5 ">= 5 documentos (5 demo del seed + re-ejecuciones)"
check_ge "$(echo "$H" | grep -o '"tenants_count":[0-9]*' | cut -d: -f2)" 2 ">= 2 empresas/tenants sembradas"

TOKEN_ADMIN=$(login "$EMAIL_ADMIN")
TOKEN_EDITOR=$(login "$EMAIL_EDITOR")
TOKEN_VIEWER=$(login "$EMAIL_VIEWER")
TOKEN_GLOBEX=$(login "$EMAIL_GLOBEX")
check "1" "$([ -n "$TOKEN_ADMIN" ] && echo 1)" "login admin@acme.com → token"
check "1" "$([ -n "$TOKEN_EDITOR" ] && echo 1)" "login editor@acme.com → token"
check "1" "$([ -n "$TOKEN_VIEWER" ] && echo 1)" "login viewer@acme.com → token"
check "1" "$([ -n "$TOKEN_GLOBEX" ] && echo 1)" "login admin@globex.com → token"

# ── 1 · Viewer ─────────────────────────────────────────────────────────────
echo ""
echo "── 1 · Viewer (viewer@acme.com) — la matriz columna viewer ──"
check "200" "$(status "$BASE/api/documents/1" -H "Authorization: Bearer $TOKEN_VIEWER")" "ve documento PÚBLICO (#1)"
check "403" "$(status "$BASE/api/documents/2" -H "Authorization: Bearer $TOKEN_VIEWER")" "NO ve privado de OTRO (#2)"
check "403" "$(status "$BASE/api/documents/3" -H "Authorization: Bearer $TOKEN_VIEWER")" "NO ve privado del editor (#3)"
check "403" "$(status "$BASE/api/documents/5" -H "Authorization: Bearer $TOKEN_VIEWER")" "NO ve doc de OTRA empresa (#5, tenancy)"
check "403" "$(status -X POST "$BASE/api/documents" -H "Authorization: Bearer $TOKEN_VIEWER" -H "Content-Type: application/json" -d '{"title":"Hack","content":"x"}')" "NO puede crear documento (scope read)"
check "403" "$(status -X POST "$BASE/api/documents/1/publish" -H "Authorization: Bearer $TOKEN_VIEWER")" "NO puede publicar"
check "403" "$(status -X DELETE "$BASE/api/documents/1" -H "Authorization: Bearer $TOKEN_VIEWER")" "NO puede borrar"
check "403" "$(status "$BASE/api/users" -H "Authorization: Bearer $TOKEN_VIEWER")" "NO puede listar usuarios (solo admin)"
check "403" "$(status -X PATCH "$BASE/api/users/3/role" -H "Authorization: Bearer $TOKEN_VIEWER" -H "Content-Type: application/json" -d '{"role":"admin"}')" "NO puede cambiar roles (la operación más sensible)"

# ── 2 · Editor ─────────────────────────────────────────────────────────────
echo ""
echo "── 2 · Editor (editor@acme.com) — la matriz columna editor ──"
check "200" "$(status "$BASE/api/documents/1" -H "Authorization: Bearer $TOKEN_EDITOR")" "ve documento PÚBLICO (#1)"
check "403" "$(status "$BASE/api/documents/2" -H "Authorization: Bearer $TOKEN_EDITOR")" "NO ve privado del admin (#2)"

# Crea un documento propio (id dinámico, re-ejecutable)
NEWDOC=$(curl -s -X POST "$BASE/api/documents" -H "Authorization: Bearer $TOKEN_EDITOR" -H "Content-Type: application/json" -d '{"title":"Borrador de prueba","content":"generado por el verificador"}')
NEWDOC_ID=$(json_id "$NEWDOC")
check "201" "$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/api/documents" -H "Authorization: Bearer $TOKEN_EDITOR" -H "Content-Type: application/json" -d '{"title":"Otro draft","content":"x"}')" "puede CREAR documento (scope write)"
check "200" "$(status -X POST "$BASE/api/documents/$NEWDOC_ID/publish" -H "Authorization: Bearer $TOKEN_EDITOR")" "puede PUBLICAR su propio documento"
check "200" "$(status -X PATCH "$BASE/api/documents/$NEWDOC_ID" -H "Authorization: Bearer $TOKEN_EDITOR" -H "Content-Type: application/json" -d '{"content":"editado por el dueño"}')" "puede EDITAR su propio documento"
check "403" "$(status -X PATCH "$BASE/api/documents/2" -H "Authorization: Bearer $TOKEN_EDITOR" -H "Content-Type: application/json" -d '{"content":"x"}')" "NO puede editar privado de OTRO (#2)"
check "403" "$(status -X DELETE "$BASE/api/documents/4" -H "Authorization: Bearer $TOKEN_EDITOR")" "NO puede borrar (solo admin)"
check "403" "$(status "$BASE/api/users" -H "Authorization: Bearer $TOKEN_EDITOR")" "NO puede listar usuarios"
check "403" "$(status -X PATCH "$BASE/api/users/3/role" -H "Authorization: Bearer $TOKEN_EDITOR" -H "Content-Type: application/json" -d '{"role":"admin"}')" "NO puede cambiar roles"

# ── 3 · Admin ──────────────────────────────────────────────────────────────
echo ""
echo "── 3 · Admin (admin@acme.com) — la matriz columna admin ──"
check "200" "$(status "$BASE/api/documents/2" -H "Authorization: Bearer $TOKEN_ADMIN")" "ve privado de OTRO (#2, es admin)"
check "200" "$(status -X PATCH "$BASE/api/documents/3" -H "Authorization: Bearer $TOKEN_ADMIN" -H "Content-Type: application/json" -d '{"content":"editado por admin"}')" "edita documento de OTRO (#3)"
check "200" "$(status "$BASE/api/users" -H "Authorization: Bearer $TOKEN_ADMIN")" "lista usuarios de su empresa"
check "200" "$(status -X DELETE "$BASE/api/documents/$NEWDOC_ID" -H "Authorization: Bearer $TOKEN_ADMIN")" "borra CUALQUIER documento (el del editor)"
check "403" "$(status "$BASE/api/documents/5" -H "Authorization: Bearer $TOKEN_ADMIN")" "NO ve doc de OTRA empresa (#5, tenancy también para admin)"
check "403" "$(status "$BASE/api/users/4" -H "Authorization: Bearer $TOKEN_ADMIN")" "NO ve usuarios de OTRA empresa (id 4 = admin de Globex)"

# Gestión de usuarios: registra uno nuevo (email único por corrida) y cambia su rol
NEW_EMAIL="alumno-$(date +%s)@ejemplo.com"
REG_FILE=$(mktemp)
REG_CODE=$(curl -s -o "$REG_FILE" -w "%{http_code}" -X POST "$BASE/api/auth/register" -H "Content-Type: application/json" -d "{\"email\":\"$NEW_EMAIL\",\"name\":\"Alumno Test\",\"password\":\"$PASS\"}")
REG_RESP=$(cat "$REG_FILE")
NEWUSER_ID=$(json_id "$REG_RESP")
check "201" "$REG_CODE" "registro de usuario nuevo (201)"
check "viewer" "$(echo "$REG_RESP" | grep -o '"role":"[^"]*"' | head -1 | cut -d'"' -f4)" "el usuario nuevo nace como viewer"
ROLE_RESP=$(curl -s -X PATCH "$BASE/api/users/$NEWUSER_ID/role" -H "Authorization: Bearer $TOKEN_ADMIN" -H "Content-Type: application/json" -d '{"role":"editor"}')
check "200" "$(curl -s -o /dev/null -w "%{http_code}" -X PATCH "$BASE/api/users/$NEWUSER_ID/role" -H "Authorization: Bearer $TOKEN_ADMIN" -H "Content-Type: application/json" -d '{"role":"editor"}')" "admin cambia el rol de un usuario"
check "editor" "$(echo "$ROLE_RESP" | grep -o '"role":"[^"]*"' | head -1 | cut -d'"' -f4)" "el rol nuevo se ve de inmediato (se relee del storage)"

# ── 4 · Scope del token (Pilar 3) ──────────────────────────────────────────
echo ""
echo "── 4 · Scope del TOKEN vs rol del USUARIO ──"
TOKEN_ADMIN_READONLY=$(login "$EMAIL_ADMIN" "read")
check "1" "$([ -n "$TOKEN_ADMIN_READONLY" ] && echo 1)" "admin loguea con scope 'read'"
check "403" "$(status -X POST "$BASE/api/documents" -H "Authorization: Bearer $TOKEN_ADMIN_READONLY" -H "Content-Type: application/json" -d '{"title":"No debería","content":"x"}')" "admin con token read-only NO puede crear (scope < rol)"
check "200" "$(status "$BASE/api/documents/1" -H "Authorization: Bearer $TOKEN_ADMIN_READONLY")" "admin con token read-only SÍ puede leer"
check "400" "$(status -X POST "$BASE/api/auth/login" -H "Content-Type: application/json" -d "{\"email\":\"$EMAIL_VIEWER\",\"password\":\"$PASS\",\"scope\":\"read write\"}")" "viewer NO puede pedir scope 'read write' (auto-elevarse)"

# ── 5 · Multi-tenancy (Globex actuando sobre Acme) ─────────────────────────
echo ""
echo "── 5 · Multi-tenancy (Globex actúa sobre Acme) ──"
check "403" "$(status "$BASE/api/documents/1" -H "Authorization: Bearer $TOKEN_GLOBEX")" "Globex NO ve públicos de Acme (#1)"
# id 1 = admin@acme.com (tenant 1). Admin de Globex no debería poder verlo.
check "403" "$(status "$BASE/api/users/1" -H "Authorization: Bearer $TOKEN_GLOBEX")" "Globex NO ve el detalle de un usuario de Acme (cross-tenant)"

# ── 6 · Autenticación básica (base: no es la lección, pero no debe romper) ─
echo ""
echo "── 6 · Autenticación básica ──"
check "401" "$(status "$BASE/api/documents/1")" "sin token → 401"
check "401" "$(status "$BASE/api/documents/1" -H "Authorization: Bearer token-invalido")" "token inválido → 401"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "RESULTADO: $PASS_OK de $PASS_TOTAL checkpoints OK"
echo "═══════════════════════════════════════════════════════════"
echo ""
if [ "$PASS_OK" = "$PASS_TOTAL" ]; then
  echo "🏆 ¡Matriz de autorización COMPLETA! Guardá esta salida como evidencia."
else
  echo "⚠️ Revisá los ❌: cada uno es un caso de la matriz que quedó abierto."
  echo "   Los checks que esperan 403 y reciben 200 son BROKEN ACCESS CONTROL (OWASP A01)."
fi
echo ""
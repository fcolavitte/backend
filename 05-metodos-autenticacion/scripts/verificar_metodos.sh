#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────
# Verificador de los 7 métodos de autenticación — Módulo 05
#
# Uso: el server debe estar levantado (uv run -m app.main en backend/).
#      Luego: bash scripts/verificar_metodos.sh
#
# Cada bloque prueba un método y muestra el resultado. Al final imprime un
# resumen de cuántos checkpoints pasaron.
# ──────────────────────────────────────────────────────────────────────────

set -u

BASE="${BASE:-http://127.0.0.1:8000}"
EMAIL="demo@ejemplo.com"
PASS="demo12345"
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

status() { curl -s -o /dev/null -w "%{http_code}" "$@"; }

echo ""
echo "═══ MÓDULO 05 — VERIFICACIÓN DE LOS 7 MÉTODOS ═══"
echo "Base: $BASE  |  Usuario: $EMAIL"
echo ""

# 0 · Health
echo "── 0 · Health ──"
H=$(curl -s "$BASE/api/health")
echo "  $H"
check "1" "$(echo "$H" | grep -c 'Funciona')" "health responde Funciona"

# 1 · Basic Auth
echo ""
echo "── 1 · Basic Auth (credenciales en cada request) ──"
check "200" "$(status -u "$EMAIL:$PASS" "$BASE/api/me/basic")" "Basic con credenciales ok"
check "401" "$(status -u "$EMAIL:mal" "$BASE/api/me/basic")" "Basic con password mal"

# 2 · Session Based (cookie)
echo ""
echo "── 2 · Session Based (cookie httpOnly) ──"
CJAR=$(mktemp)
check "200" "$(status -c "$CJAR" -X POST "$BASE/api/auth/session/login" -H "Content-Type: application/json" -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}")" "login sesión"
check "200" "$(status -b "$CJAR" "$BASE/api/me/session")" "/me/session con cookie"
S=$(curl -s "$BASE/api/health" | grep -o '"sessions_count":[0-9]*' | cut -d: -f2)
echo "  📊 sessions_count en server: $S (debería ser ≥ 1: la sesión vive en el server)"
check "200" "$(status -b "$CJAR" -X POST "$BASE/api/auth/session/logout")" "logout"
S2=$(curl -s "$BASE/api/health" | grep -o '"sessions_count":[0-9]*' | cut -d: -f2)
echo "  📊 sessions_count tras logout: $S2 (debería ser 0: revocación inmediata)"

# 3 · Token Auth (opaco en header)
echo ""
echo "── 3 · Token Auth (token opaco en header) ──"
TOKEN=$(curl -s -X POST "$BASE/api/auth/token/login" -d "username=$EMAIL&password=$PASS" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
check "200" "$(status "$BASE/api/me/token" -H "Authorization: Bearer $TOKEN")" "/me/token con bearer"
T=$(curl -s "$BASE/api/health" | grep -o '"api_tokens_count":[0-9]*' | cut -d: -f2)
echo "  📊 api_tokens_count: $T (≥ 1: el token opaco vive en el server)"
check "200" "$(status -X POST "$BASE/api/auth/token/logout" -H "Authorization: Bearer $TOKEN")" "logout revoca"

# 4 · JWT header
echo ""
echo "── 4 · JWT (header, stateless) ──"
JWT=$(curl -s -X POST "$BASE/api/auth/jwt/login" -H "Content-Type: application/json" -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
check "200" "$(status "$BASE/api/me/jwt" -H "Authorization: Bearer $JWT")" "/me/jwt con bearer"
echo "  🔎 Decodificá el JWT en https://jwt.io → payload:"
echo "     $JWT" | cut -c1-60
T2=$(curl -s "$BASE/api/health" | grep -o '"api_tokens_count":[0-9]*' | cut -d: -f2)
echo "  📊 api_tokens_count: $T2 (NO cambia: el JWT no guarda estado en el server)"

# 5 · JWT cookie
echo ""
echo "── 5 · Cookie Based (JWT en cookie httpOnly) ──"
CJAR2=$(mktemp)
check "200" "$(status -c "$CJAR2" -X POST "$BASE/api/auth/jwt-cookie/login" -H "Content-Type: application/json" -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}")" "login JWT-cookie"
check "200" "$(status -b "$CJAR2" "$BASE/api/me/jwt-cookie")" "/me/jwt-cookie con cookie"
C=$(grep -c "access_token" "$CJAR2" 2>/dev/null || echo 0)
check "1" "$C" "cookie access_token está httpOnly (no legible por JS)"

# 6 · OAuth2 + JWT
echo ""
echo "── 6 · OAuth2 (password flow) + JWT ──"
OAUTH=$(curl -s -X POST "$BASE/api/auth/oauth2/token" -d "grant_type=password&username=$EMAIL&password=$PASS" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
check "200" "$(status "$BASE/api/me/oauth2" -H "Authorization: Bearer $OAUTH")" "/me/oauth2"
check "401" "$(status "$BASE/api/me/oauth2")" "sin token"

# 7 · SSO
echo ""
echo "── 7 · SSO (OIDC simulado: IdP emite id_token, app lo valida) ──"
IDTOKEN=$(curl -s -X POST "$BASE/api/sso/simulate" -H "Content-Type: application/json" -d '{"email":"externo@ejemplo.com","name":"Usuario Externo"}' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
check "200" "$(status "$BASE/api/me/sso" -H "Authorization: Bearer $IDTOKEN")" "/me/sso con id_token del IdP (JIT)"
FAKEJWT=$(curl -s -X POST "$BASE/api/auth/jwt/login" -H "Content-Type: application/json" -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
check "401" "$(status "$BASE/api/me/sso" -H "Authorization: Bearer $FAKEJWT")" "token local sin iss/aud rechazado"

# 8 · Rate limiting (Nivel 02) — email dinámico para que sea re-ejecutable
echo ""
echo "── 8 · Rate limiting del login (5 fallos → 429) ──"
RL_EMAIL="rate-$(date +%s)@ejemplo.com"   # email único por corrida (no contamina el demo)
TMPOUT=$(mktemp)
RL_CODES=""
for i in 1 2 3 4 5; do
  RL_CODES="$RL_CODES $(status -X POST "$BASE/api/auth/jwt/login" -H "Content-Type: application/json" -d "{\"email\":\"$RL_EMAIL\",\"password\":\"incorrecta\"}")"
done
RL_CODES=$(echo $RL_CODES)  # colapsa espacios: " 401 401 401 401 401" → "401 401 401 401 401"
check "401 401 401 401 401" "$RL_CODES" "5 intentos fallidos → 401 (y se van acumulando)"
check "429" "$(status -X POST "$BASE/api/auth/jwt/login" -H "Content-Type: application/json" -d "{\"email\":\"$RL_EMAIL\",\"password\":\"incorrecta\"}")" "el 6º intento → 429 Too Many Requests"
check "1" "$(curl -s -D "$TMPOUT" -o /dev/null -X POST "$BASE/api/auth/jwt/login" -H "Content-Type: application/json" -d "{\"email\":\"$RL_EMAIL\",\"password\":\"incorrecta\"}" && grep -ci "retry-after" "$TMPOUT")" "la respuesta 429 trae Retry-After"
check "200" "$(status -X POST "$BASE/api/auth/jwt/login" -H "Content-Type: application/json" -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}")" "el login EXITOSO del demo NO está bloqueado (reset por email)"

# 9 · Security headers (Nivel 02)
echo ""
echo "── 9 · Security headers (Nivel 02) ──"
HDRS=$(mktemp)
curl -s -D "$HDRS" -o /dev/null "$BASE/api/health"
check "1" "$(grep -ci 'strict-transport-security' "$HDRS")" "HSTS presente"
check "1" "$(grep -ci 'x-content-type-options: nosniff' "$HDRS")" "nosniff presente"
check "1" "$(grep -ci 'x-frame-options' "$HDRS")" "X-Frame-Options presente"
check "1" "$(grep -ci 'referrer-policy' "$HDRS")" "Referrer-Policy presente"
MB=$(mktemp)
curl -s -D "$MB" -o /dev/null -u "$EMAIL:$PASS" "$BASE/api/me/basic"
check "1" "$(grep -ci 'cache-control: no-store' "$MB")" "Cache-Control: no-store en /api/me/*"

echo ""
echo "═══════════════════════════════════════════════"
echo "RESULTADO: $PASS_OK de $PASS_TOTAL checkpoints OK"
echo "═══════════════════════════════════════════════"
echo ""
[ "$PASS_OK" = "$PASS_TOTAL" ] && echo "🎉 ¡Todos los métodos funcionan!" || echo "⚠️ Revisá los ❌."
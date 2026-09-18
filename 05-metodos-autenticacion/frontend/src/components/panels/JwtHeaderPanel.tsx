import { useState } from "react";
import { jwtLogin, jwtMe } from "../../api";
import type { ApiResult, Token, UserRead } from "../../types";
import { AuthForm, PanelShell, ProfileCard, ResultBox } from "./shared";

/**
 * Método 4 — JWT EN HEADER (stateless).
 *
 * El token NO es opaco: es un JWT firmado (header.payload.signature) que
 * lleva la info adentro. El server NO guarda nada: decodifica y verifica
 * la firma en cada request. Por eso el HealthBar NO cambia con este método.
 *
 * El payload está SOLO codificado (base64url), no cifrado. El botón
 * "decodificar" lo demuestra: cualquiera puede leerlo SIN la firma.
 * Por eso nunca ponés passwords ni datos sensibles en un JWT.
 */

function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const part = token.split(".")[1];
    if (!part) return null;
    const json = atob(part.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(decodeURIComponent(escape(json)));
  } catch {
    return null;
  }
}

export default function JwtHeaderPanel() {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserRead | null>(null);
  const [result, setResult] = useState<ApiResult<Token | UserRead | unknown> | null>(null);
  const [busyLogin, setBusyLogin] = useState(false);
  const [busy, setBusy] = useState(false);
  const [payload, setPayload] = useState<Record<string, unknown> | null>(null);

  async function handleLogin(email: string, password: string) {
    setBusyLogin(true);
    const res = await jwtLogin(email, password);
    setBusyLogin(false);
    setResult(res);
    const jwt = res.ok && res.data ? res.data.access_token : null;
    setToken(jwt);
    setPayload(jwt ? decodeJwtPayload(jwt) : null);
    setUser(null);
  }

  async function handleMe() {
    if (!token) return;
    setBusy(true);
    const res = await jwtMe(token);
    setResult(res);
    setUser(res.ok && res.data ? (res.data as UserRead) : null);
    setBusy(false);
  }

  return (
    <PanelShell
      numero="4"
      titulo="JWT en header (stateless)"
      leccion={
        <>
          El JWT <strong>lleva la info adentro</strong> (payload) y está firmado.
          El server NO guarda nada → el HealthBar <strong>no cambia</strong>.
          Pero ojo: el payload es legible sin la firma. Probá el botón
          "decodificar" — es base64url, no cifrado. Solo identifica (sub) y
          expiración; NUNCA pongas un password adentro.
        </>
      }
    >
      <div className="step">
        <h3>1 · Login</h3>
        <AuthForm onSubmit={handleLogin} submitLabel="POST /api/auth/jwt/login" busy={busyLogin} />
        {token && (
          <>
            <p className="token-preview">
              Tu JWT: <code className="wrap">{token.slice(0, 40)}…</code>
            </p>
            <button onClick={() => setPayload((p) => (p ? null : decodeJwtPayload(token)))}>
              {payload ? "Ocultar payload" : "Decodificar payload (sin el secreto!)"}
            </button>
            {payload && (
              <pre className="decoded-jwt">{JSON.stringify(payload, null, 2)}</pre>
            )}
          </>
        )}
      </div>

      <div className="step">
        <h3>2 · ¿Quién soy?</h3>
        <button onClick={handleMe} disabled={busy || !token}>
          GET /api/me/jwt (Bearer header)
        </button>
      </div>

      <ResultBox result={result} />
      <ProfileCard user={user} />
    </PanelShell>
  );
}
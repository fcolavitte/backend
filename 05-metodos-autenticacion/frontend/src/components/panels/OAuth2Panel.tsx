import { useState } from "react";
import { oauth2Me, oauth2Token } from "../../api";
import type { ApiResult, Token, UserRead } from "../../types";
import { AuthForm, PanelShell, ProfileCard, ResultBox } from "./shared";

/**
 * Método 6 — OAUTH 2.0 (password flow) con JWT como access token.
 *
 * ESTE es el patrón del tutorial oficial de FastAPI. Es la COMBINACIÓN:
 *
 *   - OAuth 2.0 = el PROTOCOLO (flujo, grant types, endpoint /token).
 *   - JWT       = el FORMATO del access token.
 *   - Bearer    = el ESQUEMA de transporte (header Authorization).
 *
 * Mirá el contrato: POST form-urlencoded CON grant_type=password. Eso es
 * OAuth2 (el protocolo). El token que devuelve es un JWT (el formato).
 * Podés tener OAuth2 con tokens opacos (método 3) o con JWT (acá).
 */

export default function OAuth2Panel() {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserRead | null>(null);
  const [result, setResult] = useState<ApiResult<Token | UserRead | unknown> | null>(null);
  const [busyLogin, setBusyLogin] = useState(false);
  const [busy, setBusy] = useState(false);

  async function handleLogin(email: string, password: string) {
    setBusyLogin(true);
    const res = await oauth2Token(email, password);
    setBusyLogin(false);
    setResult(res);
    setToken(res.ok && res.data ? res.data.access_token : null);
    setUser(null);
  }

  async function handleMe() {
    if (!token) return;
    setBusy(true);
    const res = await oauth2Me(token);
    setResult(res);
    setUser(res.ok && res.data ? (res.data as UserRead) : null);
    setBusy(false);
  }

  return (
    <PanelShell
      numero="6"
      titulo="OAuth 2.0 (password flow) + JWT"
      leccion={
        <>
          El patrón que enseña el tutorial oficial de FastAPI. El login es un{" "}
          <code>POST /token</code> form-urlencoded con{" "}
          <code>grant_type=password</code> — ESO es OAuth2 (el protocolo). El
          token que devuelve es un <strong>JWT</strong> firmado (el formato).
          En producción se suma el refresh token con rotación, y los flows de
          terceros (authorization code + PKCE) para "Login with Google".
        </>
      }
    >
      <div className="step">
        <h3>1 · POST /api/auth/oauth2/token</h3>
        <AuthForm onSubmit={handleLogin} submitLabel="grant_type=password" busy={busyLogin} />
        {token && (
          <p className="token-preview">
            access_token (JWT): <code className="wrap">{token.slice(0, 40)}…</code>
          </p>
        )}
      </div>

      <div className="step">
        <h3>2 · ¿Quién soy?</h3>
        <button onClick={handleMe} disabled={busy || !token}>
          GET /api/me/oauth2 (Bearer header)
        </button>
      </div>

      <ResultBox result={result} />
      <ProfileCard user={user} />
    </PanelShell>
  );
}
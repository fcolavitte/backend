import { useState } from "react";
import { tokenLogin, tokenLogout, tokenMe } from "../../api";
import type { ApiResult, Token, UserRead } from "../../types";
import { AuthForm, PanelShell, ProfileCard, ResultBox } from "./shared";

/**
 * Método 3 — TOKEN AUTH (token opaco en header).
 *
 * Igual filosofía que Session: el server guarda estado. Pero el token viaja
 * en el header `Authorization: Bearer <token>` en vez de una cookie. Es la
 * autenticación típica de APIs para clientes que NO son un navegador
 * (apps móviles, otras APIs, CLIs).
 *
 * El token es OPACO: un string aleatorio sin significado adentro. Logout
 * revoca en el server. Mirá el HealthBar: api_tokens_count sube SOLO acá.
 *
 * En el código FIJATE: login por form-urlencoded (no JSON) y el token lo
 * guardamos en el estado de React (memoria), NO en localStorage.
 */

export default function TokenPanel() {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserRead | null>(null);
  const [result, setResult] = useState<ApiResult<Token | UserRead | unknown> | null>(null);
  const [busyLogin, setBusyLogin] = useState(false);
  const [busy, setBusy] = useState(false);

  async function handleLogin(email: string, password: string) {
    setBusyLogin(true);
    const res = await tokenLogin(email, password);
    setBusyLogin(false);
    setResult(res);
    setToken(res.ok && res.data ? res.data.access_token : null);
    setUser(null);
  }

  async function handleMe() {
    if (!token) return;
    setBusy(true);
    const res = await tokenMe(token);
    setResult(res);
    setUser(res.ok && res.data ? (res.data as UserRead) : null);
    setBusy(false);
  }

  async function handleLogout() {
    if (!token) return;
    setBusy(true);
    const res = await tokenLogout(token);
    setResult(res);
    setBusy(false);
    setToken(null);
    setUser(null);
  }

  return (
    <PanelShell
      numero="3"
      titulo="Token Auth (opaco, en header)"
      leccion={
        <>
          Login form-urlencoded → el server crea un token <strong>opaco</strong>{" "}
          (aleatorio, sin significado) y lo guarda. En cada request lo mandás en{" "}
          <code>Authorization: Bearer &lt;token&gt;</code>. El token vive en{" "}
          <strong>memoria</strong> (estado de React), NO en localStorage. Mirá{" "}
          <strong>tokens opacos</strong> en el HealthBar: sube SOLO con este método.
        </>
      }
    >
      <div className="step">
        <h3>1 · Login</h3>
        <AuthForm onSubmit={handleLogin} submitLabel="POST /api/auth/token/login" busy={busyLogin} />
        {token && (
          <p className="token-preview">
            Tu token opaco (guardado en memoria por el front):{" "}
            <code className="wrap">{token.slice(0, 24)}…</code>
          </p>
        )}
      </div>

      <div className="step">
        <h3>2 · ¿Quién soy?</h3>
        <button onClick={handleMe} disabled={busy || !token}>
          GET /api/me/token (Bearer header)
        </button>
      </div>

      <div className="step">
        <h3>3 · Logout</h3>
        <button onClick={handleLogout} disabled={busy || !token}>
          POST /api/auth/token/logout (revoca en el server)
        </button>
      </div>

      <ResultBox result={result} />
      <ProfileCard user={user} />
    </PanelShell>
  );
}
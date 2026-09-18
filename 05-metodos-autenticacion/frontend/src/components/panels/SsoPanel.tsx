import { useState } from "react";
import { ssoExplain, ssoMe, ssoSimulate } from "../../api";
import type { ApiResult, SSOExplain, Token, UserRead } from "../../types";
import { PanelShell, ProfileCard, ResultBox } from "./shared";

/**
 * Método 7 — SSO (Single Sign-On, OIDC simulado).
 *
 * SSO es la EXPERIENCIA: te logueás una vez en un proveedor (Google,
 * Keycloak, tu empresa) y entrás a VARIOS servicios sin volver a loguearte.
 * Se implementa con OIDC (sobre OAuth 2.0): el IdP emite un id_token (JWT).
 *
 * Como no podemos levantar un IdP real en un módulo autocontenido, lo
 * simulamos de forma didáctica y HONESTA: POST /api/sso/simulate actúa como
 * el IdP emitiendo un JWT con claims OIDC (iss, aud, sub, email). Después,
 * GET /api/me/sso valida firma + iss + aud y hace JIT provisioning.
 *
 * Probalo con un email NUEVO: mirá users_count subir en el HealthBar — se
 * creó el usuario local al vuelo.
 */

export default function SsoPanel() {
  const [email, setEmail] = useState("demo@ejemplo.com");
  const [name, setName] = useState("Demo SSO");
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserRead | null>(null);
  const [result, setResult] = useState<ApiResult<Token | UserRead | unknown> | null>(null);
  const [explain, setExplain] = useState<ApiResult<SSOExplain> | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSimulate() {
    setBusy(true);
    const res = await ssoSimulate(email.trim(), name.trim());
    setResult(res);
    setToken(res.ok && res.data ? res.data.access_token : null);
    setUser(null);
    setBusy(false);
  }

  async function handleValidate() {
    if (!token) return;
    setBusy(true);
    const res = await ssoMe(token);
    setResult(res);
    setUser(res.ok && res.data ? (res.data as UserRead) : null);
    setBusy(false);
  }

  async function handleExplain() {
    setBusy(true);
    const res = await ssoExplain();
    setExplain(res);
    setBusy(false);
  }

  return (
    <PanelShell
      numero="7"
      titulo="SSO (OIDC simulado)"
      leccion={
        <>
          El IdP (simulado) emite un <code>id_token</code> con claims OIDC:{" "}
          <code>iss</code> (quién lo emitió), <code>aud</code> (para quién),
          <code> sub/email/name</code>. Nuestra app lo valida (firma + iss +
          aud) y hace <strong>JIT provisioning</strong>: si el email no existe,
          crea el usuario local al vuelo. Probalo con un email nuevo y mirá el
          HealthBar.
        </>
      }
    >
      <div className="step">
        <h3>0 · Flujo OIDC de verdad (para leer primero)</h3>
        <button onClick={handleExplain} disabled={busy}>
          GET /api/sso/explain — el flujo en 7 pasos
        </button>
        {explain?.ok && explain.data && (
          <ol className="oidc-steps">
            {explain.data.steps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        )}
      </div>

      <div className="step">
        <h3>1 · El IdP emite el id_token (simulado)</h3>
        <div className="auth-form">
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="email@ejemplo.com"
          />
          <input
            type="text"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Nombre (claim name)"
          />
          <button onClick={handleSimulate} disabled={busy || !email.trim()}>
            POST /api/sso/simulate (emitir id_token)
          </button>
        </div>
        {token && (
          <p className="token-preview">
            id_token del IdP: <code className="wrap">{token.slice(0, 40)}…</code>
          </p>
        )}
      </div>

      <div className="step">
        <h3>2 · Tu app valida el token del tercero</h3>
        <button onClick={handleValidate} disabled={busy || !token}>
          GET /api/me/sso (firma + iss + aud → JIT provisioning)
        </button>
      </div>

      <ResultBox result={result} />
      <ProfileCard user={user} />
    </PanelShell>
  );
}
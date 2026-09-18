import { useState } from "react";
import { jwtCookieLogin, jwtCookieLogout, jwtCookieMe } from "../../api";
import type { ApiResult, UserRead } from "../../types";
import { AuthForm, PanelShell, ProfileCard, ResultBox } from "./shared";

/**
 * Método 5 — COOKIE BASED (JWT en cookie httpOnly).
 *
 * El MISMO JWT del método 4, pero el vehículo cambia: en vez del header
 * Authorization, viaja en una cookie httpOnly.
 *
 * ¿Por qué importa el vehículo?
 *   - Header + localStorage (SPA): vulnerable a XSS (un script inyectado
 *     lee el localStorage y roba el token).
 *   - Cookie httpOnly: el JS NO la puede leer → mitiga XSS. PERO abre
 *     CSRF (el browser envía la cookie sola en requests cross-site), que
 *     se mitiga con SameSite + token anti-CSRF.
 *
 * Tradeoff: elegís qué ataque mitigás (XSS vs CSRF). No hay "la mejor".
 */

export default function JwtCookiePanel() {
  const [user, setUser] = useState<UserRead | null>(null);
  const [result, setResult] = useState<ApiResult<UserRead> | null>(null);
  const [loginInfo, setLoginInfo] = useState<ApiResult<unknown> | null>(null);
  const [logoutMsg, setLogoutMsg] = useState<ApiResult<unknown> | null>(null);
  const [busyLogin, setBusyLogin] = useState(false);
  const [busy, setBusy] = useState(false);

  async function handleLogin(email: string, password: string) {
    setBusyLogin(true);
    setLoginInfo(null);
    setLogoutMsg(null);
    const res = await jwtCookieLogin(email, password);
    setBusyLogin(false);
    if (res.ok) {
      setLoginInfo({
        ok: true,
        status: 200,
        data: {
          leccion:
            "La cookie access_token (con el JWT adentro) la guardó el browser como httpOnly. Mirala en DevTools → Application → Cookies.",
          "document.cookie": document.cookie || "(vacío — httpOnly, invisible al JS)",
        },
      });
    }
  }

  async function handleMe() {
    setBusy(true);
    const res = await jwtCookieMe();
    setResult(res);
    setUser(res.ok && res.data ? res.data : null);
    setBusy(false);
  }

  async function handleLogout() {
    setBusy(true);
    setLogoutMsg(null);
    const res = await jwtCookieLogout();
    setLogoutMsg(res);
    setBusy(false);
  }

  return (
    <PanelShell
      numero="5"
      titulo="Cookie Based (JWT en cookie httpOnly)"
      leccion={
        <>
          El mismo JWT, otro vehículo: una cookie <strong>httpOnly</strong>.
          El JS no puede leerla (mitiga XSS) pero el browser la manda sola en
          cada request. El logout <strong>solo borra la cookie</strong>: el JWT
          sigue válido hasta expirar (no hay estado en el server que borrar).
        </>
      }
    >
      <div className="step">
        <h3>1 · Login</h3>
        <AuthForm onSubmit={handleLogin} submitLabel="POST /api/auth/jwt-cookie/login" busy={busyLogin} />
        {loginInfo && <ResultBox result={loginInfo} />}
      </div>

      <div className="step">
        <h3>2 · ¿Quién soy?</h3>
        <button onClick={handleMe} disabled={busy}>
          GET /api/me/jwt-cookie (la cookie viaja sola)
        </button>
      </div>

      <ResultBox result={result} />
      <ProfileCard user={user} />

      <div className="step">
        <h3>3 · Logout</h3>
        <button onClick={handleLogout} disabled={busy}>
          POST /api/auth/jwt-cookie/logout (borra la cookie)
        </button>
        {logoutMsg && <ResultBox result={logoutMsg} />}
      </div>
    </PanelShell>
  );
}
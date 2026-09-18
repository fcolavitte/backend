import { useState } from "react";
import { sessionLogin, sessionLogout, sessionMe } from "../../api";
import type { ApiResult, UserRead } from "../../types";
import { AuthForm, PanelShell, ProfileCard, ResultBox } from "./shared";

/**
 * Método 2 — SESSION BASED.
 *
 * El login crea una sesión EN EL SERVER y la guarda en una cookie httpOnly.
 * El browser guarda y reenvía la cookie SOLA: el JavaScript no puede leerla
 * (la pestaña Application de DevTools sí la muestra — probalo).
 * Logout borra la sesión del server → revocación INMEDIATA.
 *
 * Mirá el HealthBar: sessions_count sube PEEEEROOO solo con este método.
 */

export default function SessionPanel() {
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
    const res = await sessionLogin(email, password);
    setBusyLogin(false);
    // Si el login salió bien, la cookie ya está en el browser. Veamos si el
    // JS puede (no puede) leerla.
    if (res.ok) {
      setLoginInfo({
        ok: true,
        status: 200,
        data: {
          "document.cookie": document.cookie || "(vacío — la cookie es httpOnly, el JS NO puede leerla)",
          leccion:
            "La cookie session_id la guardó el browser. Abrí DevTools → Application → Cookies para verla.",
        },
      });
    }
  }

  async function handleMe() {
    setBusy(true);
    const res = await sessionMe();
    setResult(res);
    setUser(res.ok && res.data ? res.data : null);
    setBusy(false);
  }

  async function handleLogout() {
    setBusy(true);
    setLogoutMsg(null);
    const res = await sessionLogout();
    setLogoutMsg(res);
    setBusy(false);
  }

  return (
    <PanelShell
      numero="2"
      titulo="Session Based (cookie httpOnly)"
      leccion={
        <>
          Login → el server crea la sesión y responde con la cookie{" "}
          <code>session_id</code> (httpOnly: invisible al JS). Después, cada
          request la manda <strong>sola</strong>, sin tocar nada en el código.
          Logout = revocación inmediata (el server la borra). Mirá el contador{" "}
          <strong>sesiones</strong> en el HealthBar.
        </>
      }
    >
      <div className="step">
        <h3>1 · Login</h3>
        <AuthForm onSubmit={handleLogin} submitLabel="POST /api/auth/session/login" busy={busyLogin} />
        {loginInfo && <ResultBox result={loginInfo} />}
      </div>

      <div className="step">
        <h3>2 · ¿Quién soy?</h3>
        <button onClick={handleMe} disabled={busy}>
          GET /api/me/session (la cookie viaja sola)
        </button>
      </div>

      <ResultBox result={result} />
      <ProfileCard user={user} />

      <div className="step">
        <h3>3 · Logout</h3>
        <button onClick={handleLogout} disabled={busy}>
          POST /api/auth/session/logout (revocación inmediata)
        </button>
        {logoutMsg && <ResultBox result={logoutMsg} />}
      </div>
    </PanelShell>
  );
}
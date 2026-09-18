import { useState } from "react";
import { login, register } from "../api";
import type { ApiResult, Token } from "../types";

/** Un usuario demo del seed (storage.py): login en un click. */
const DEMO_USERS = [
  { email: "admin@acme.com", role: "admin", tenant: "Acme", color: "badge-admin" },
  { email: "editor@acme.com", role: "editor", tenant: "Acme", color: "badge-editor" },
  { email: "viewer@acme.com", role: "viewer", tenant: "Acme", color: "badge-viewer" },
  { email: "admin@globex.com", role: "admin", tenant: "Globex", color: "badge-admin" },
];

const DEMO_PASSWORD = "demo12345";

interface Props {
  onLoggedIn: (token: string) => void;
}

/**
 * Login con los 4 usuarios demo (1 click) + login manual + register
 * (collapsible). El selector de SCOPE es LA pieza didáctica de este panel:
 *
 *   - default        → el server le asigna el scope del rol
 *   - read           → token SOLO LECTURA (aunque seas admin)
 *   - read write     → lectura + escritura
 *
 * Probalo: admin logueado con scope "read" → la UI y el server deben
 * frenar cualquier escritura. Ese límite vive en el TOKEN, no en el rol.
 */
export default function LoginPanel({ onLoggedIn }: Props) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [scope, setScope] = useState<string>("default");
  const [error, setError] = useState<string | null>(null);

  // register
  const [regEmail, setRegEmail] = useState("");
  const [regName, setRegName] = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [regMessage, setRegMessage] = useState<string | null>(null);

  function doLogin(e: string, p: string, sc: string) {
    setError(null);
    const scopeArg = sc === "default" ? null : sc;
    void login(e, p, scopeArg).then((res: ApiResult<Token>) => {
      if (res.ok && res.data) {
        onLoggedIn(res.data.access_token);
      } else {
        setError(res.detail ?? "No se pudo iniciar sesión");
      }
    });
  }

  function quickLogin(usr: (typeof DEMO_USERS)[number]) {
    setEmail(usr.email);
    setPassword(DEMO_PASSWORD);
    setScope("default");
    doLogin(usr.email, DEMO_PASSWORD, "default");
  }

  function doRegister() {
    setRegMessage(null);
    void register(regEmail, regName, regPassword).then((res) => {
      if (res.ok) {
        setRegMessage(`201 — ${res.data?.email} creado (viewer). Ahora logueate.`);
        setRegEmail("");
        setRegName("");
        setRegPassword("");
      } else {
        setRegMessage(`${res.status}: ${res.detail}` ?? "Error");
      }
    });
  }

  return (
    <div>
      <h2>Ingresá al laboratorio</h2>

      <div className="demo-grid">
        {DEMO_USERS.map((usr) => (
          <button
            key={usr.email}
            className={`demo-user ${usr.color}`}
            onClick={() => quickLogin(usr)}
          >
            <span className="demo-email">{usr.email}</span>
            <span className="demo-meta">
              {usr.role} · {usr.tenant}
            </span>
          </button>
        ))}
      </div>

      <div className="form-row">
        <label>
          Scope del token
          <select value={scope} onChange={(ev) => setScope(ev.target.value)}>
            <option value="default">default (el del rol)</option>
            <option value="read">read — SOLO LECTURA</option>
            <option value="read write">read write — lectura + escritura</option>
          </select>
        </label>
      </div>

      <form
        className="login-form"
        onSubmit={(ev) => {
          ev.preventDefault();
          doLogin(email, password, scope);
        }}
      >
        <div className="form-row">
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(ev) => setEmail(ev.target.value)}
              placeholder="admin@acme.com"
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(ev) => setPassword(ev.target.value)}
              placeholder="demo12345"
              required
            />
          </label>
        </div>
        <button className="btn primary" type="submit">
          Ingresar
        </button>
        {error && <p className="error">{error}</p>}
      </form>

      <details className="register-box">
        <summary>¿Sin usuario? Registrate (nace como viewer)</summary>
        <div className="form-row">
          <label>
            Email
            <input
              type="email"
              value={regEmail}
              onChange={(ev) => setRegEmail(ev.target.value)}
              placeholder="alumno@facultad.edu"
            />
          </label>
          <label>
            Nombre
            <input
              type="text"
              value={regName}
              onChange={(ev) => setRegName(ev.target.value)}
              placeholder="Tu nombre"
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={regPassword}
              onChange={(ev) => setRegPassword(ev.target.value)}
              placeholder="mínimo 8 caracteres"
            />
          </label>
        </div>
        <button className="btn" type="button" onClick={doRegister}>
          Registrarme
        </button>
        {regMessage && <p className="ok">{regMessage}</p>}
      </details>
    </div>
  );
}
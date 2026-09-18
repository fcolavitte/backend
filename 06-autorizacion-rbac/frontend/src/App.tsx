import { useEffect, useState } from "react";
import { decodeToken, setLogSink } from "./api";
import HealthBar from "./components/HealthBar";
import LoginPanel from "./components/LoginPanel";
import SessionInfo from "./components/SessionInfo";
import UsersPanel from "./components/UsersPanel";
import DocumentsPanel from "./components/DocumentsPanel";
import ProberPanel from "./components/ProberPanel";
import RequestLog from "./components/RequestLog";
import { canManageUsers } from "./authz";
import type { JwtPayload, LogEntry } from "./types";

/**
 * Laboratorio del Módulo 06 — Autorización RBAC.
 *
 * El backend recién tiene sentido con un cliente: acá probás la MATRIZ
 * en vivo con los 4 usuarios demo y mirás cómo responde el server
 * (200 vs 403) ANTES y DESPUÉS de completar tu entrega.
 *
 * Estructura:
 *   - HealthBar: contadores del server (seed en memoria).
 *   - LoginPanel: entrá con los usuarios demo (un click) o manual;
 *     el selector de SCOPE limita lo que ESTE token puede hacer.
 *   - SessionInfo: el payload del JWT decodificado — legible sin secreto.
 *   - ProberPanel: el probador de la matriz. Acá ves el IDOR en vivo:
 *     logueate como viewer y pedí GET /api/documents/5 (plan Globex).
 *   - UsersPanel (solo admin): gestión de usuarios y roles.
 *   - DocumentsPanel: el CRUD de documentos con acciones contextuales.
 *   - Consola abajo: cada request con su status. El status ES la lección.
 */

const STORAGE_KEY = "mod06_token";

export default function App() {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem(STORAGE_KEY),
  );
  const [payload, setPayload] = useState<JwtPayload | null>(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? decodeToken(saved) : null;
  });
  const [log, setLog] = useState<LogEntry[]>([]);

  // El api.ts emite cada request a este sink; lo mostramos en la consola.
  useEffect(() => {
    setLogSink((entry) => {
      setLog((prev) => [...prev.slice(-199), entry]);
    });
  }, []);

  // Si el token que teníamos guardado está corrupto, lo descartamos.
  useEffect(() => {
    if (token && !payload) {
      localStorage.removeItem(STORAGE_KEY);
      setToken(null);
    }
  }, [token, payload]);

  function handleLoggedIn(accessToken: string) {
    const decoded = decodeToken(accessToken);
    if (!decoded) return;
    localStorage.setItem(STORAGE_KEY, accessToken);
    setToken(accessToken);
    setPayload(decoded);
  }

  function handleLogout() {
    localStorage.removeItem(STORAGE_KEY);
    setToken(null);
    setPayload(null);
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Laboratorio — Autorización RBAC</h1>
        <p className="subtitle">
          {payload ? (
            <>
              Sesión activa como <strong>{payload.sub}</strong> · rol{" "}
              <strong>{payload.role}</strong> · tenant{" "}
              <strong>{payload.tenant_id}</strong> · scope{" "}
              <strong>{payload.scope}</strong>
            </>
          ) : (
            <>
              Usuarios demo (password <code>demo12345</code>):{" "}
              <code>admin@acme.com</code> · <code>editor@acme.com</code> ·{" "}
              <code>viewer@acme.com</code> · <code>admin@globex.com</code>
            </>
          )}
        </p>
      </header>

      <HealthBar />

      {!payload && (
        <main className="login-area">
          <LoginPanel onLoggedIn={handleLoggedIn} />
        </main>
      )}

      {payload && token && (
        <main className="panel-area">
          <div className="grid-2">
            <section className="card">
              <SessionInfo payload={payload} onLogout={handleLogout} />
            </section>
            <section className="card">
              <ProberPanel token={token} payload={payload} />
            </section>
          </div>

          {canManageUsers(payload.role) && (
            <section className="card">
              <UsersPanel
                token={token}
                currentUserId={Number(payload.sub)}
                currentRole={payload.role}
              />
            </section>
          )}

          <section className="card">
            <DocumentsPanel token={token} payload={payload} />
          </section>
        </main>
      )}

      <RequestLog entries={log} />

      <footer className="app-footer">
        Módulo 06 · Recordá: ocultar un botón NO es seguridad — la matriz se
        decide en el SERVER. Mirá el status de cada request en la consola.
      </footer>
    </div>
  );
}
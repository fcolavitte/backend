import { useEffect, useState } from "react";
import { setLogSink } from "./api";
import HealthBar from "./components/HealthBar";
import RequestLog from "./components/RequestLog";
import BasicPanel from "./components/panels/BasicPanel";
import SessionPanel from "./components/panels/SessionPanel";
import TokenPanel from "./components/panels/TokenPanel";
import JwtHeaderPanel from "./components/panels/JwtHeaderPanel";
import JwtCookiePanel from "./components/panels/JwtCookiePanel";
import OAuth2Panel from "./components/panels/OAuth2Panel";
import SsoPanel from "./components/panels/SsoPanel";
import RateLimitPanel from "./components/panels/RateLimitPanel";
import type { LogEntry } from "./types";

/**
 * Laboratorio del Módulo 05 — probá los 7 métodos de autenticación.
 *
 * Estructura didáctica:
 *
 *   - HealthBar arriba: los contadores del server en vivo. La lección
 *     visible: qué métodos guardan estado (2 y 3) y cuáles no (1, 4...).
 *   - Tabs: un panel por método + el panel de rate limiting.
 *   - Consola abajo: cada request con su status. Hacé 5 logins mal y
 *     mirá el 429.
 *
 * Usuario demo: demo@ejemplo.com / demo12345
 */

const TABS = [
  { id: "basic", label: "1 · Basic", panel: <BasicPanel /> },
  { id: "session", label: "2 · Session (cookie)", panel: <SessionPanel /> },
  { id: "token", label: "3 · Token opaco", panel: <TokenPanel /> },
  { id: "jwt-header", label: "4 · JWT header", panel: <JwtHeaderPanel /> },
  { id: "jwt-cookie", label: "5 · JWT cookie", panel: <JwtCookiePanel /> },
  { id: "oauth2", label: "6 · OAuth2", panel: <OAuth2Panel /> },
  { id: "sso", label: "7 · SSO", panel: <SsoPanel /> },
  { id: "rate", label: "8 · Rate limit", panel: <RateLimitPanel /> },
];

export default function App() {
  const [activeTab, setActiveTab] = useState<string>("basic");
  const [log, setLog] = useState<LogEntry[]>([]);

  // El api.ts emite cada request a este sink; lo mostramos en la consola.
  useEffect(() => {
    setLogSink((entry) => {
      setLog((prev) => [...prev.slice(-199), entry]);
    });
  }, []);

  const activePanel = TABS.find((tab) => tab.id === activeTab)?.panel;

  return (
    <div className="app">
      <header className="app-header">
        <h1>Laboratorio — 7 métodos de autenticación</h1>
        <p className="subtitle">
          Usuario demo: <code>demo@ejemplo.com</code> / <code>demo12345</code> — probá
          cada método y mirá los contadores arriba.
        </p>
      </header>

      <HealthBar />

      <nav className="tabs" role="tablist">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={activeTab === tab.id}
            className={activeTab === tab.id ? "active" : ""}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <main className="panel-area">{activePanel}</main>

      <RequestLog entries={log} />

      <footer className="app-footer">
        Módulo 05 · Desarrollá el hábito de mirar la pestaña Network del DevTools.
      </footer>
    </div>
  );
}
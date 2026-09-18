import { useState } from "react";
import {
  deleteDocument,
  getDocument,
  listUsers,
  publishDocument,
  updateDocument,
} from "../api";
import type { JwtPayload } from "../types";

interface Props {
  token: string;
  payload: JwtPayload;
}

interface ProbeResult {
  method: string;
  path: string;
  status: number;
  body: unknown;
}

/**
 * Probador de la matriz — el widget que PRUEBA el backend en vivo.
 *
 * Elegí un ID de documento (o escribí uno propio) y mandá las
 * peticiones. Mirá el status que responde el server ANTES y DESPUÉS
 * de completar tus dependencias de autorización.
 *
 * Casos célebres:
 *   Doc 1 → público de Acme (todos lo ven)
 *   Doc 2 → privado de admin Acme (editor ve 403)
 *   Doc 3 → privado de editor Acme (admin lo ve 200)
 *   Doc 5 → privado de Globex (cross-tenant → 403 para Acme)
 *   Doc 999 → no existe → 404 siempre
 *
 * 🔴 IDOR: logueate como viewer y pedí GET doc 5 (plan Globex).
 *    Si da 200 → tu backend está vulnerable (dependencies.py incompleto).
 *    Si da 403 → lo hiciste bien (object-level + tenancy).
 */
export default function ProberPanel({ token, payload }: Props) {
  const [docId, setDocId] = useState("1");
  const [result, setResult] = useState<ProbeResult | null>(null);

  function probe(method: string, path: string, fetcher: () => Promise<{ status: number; data: unknown }>) {
    setResult(null);
    void fetcher().then((res) => {
      setResult({ method, path, status: res.status, body: res.data });
    });
  }

  function doGet() {
    const id = Number(docId);
    probe("GET", `/api/documents/${id}`, () => getDocument(token, id));
  }

  function doPatch() {
    const id = Number(docId);
    probe("PATCH", `/api/documents/${id}`, () =>
      updateDocument(token, id, { title: "HACK" }),
    );
  }

  function doPublish() {
    const id = Number(docId);
    probe("POST", `/api/documents/${id}/publish`, () => publishDocument(token, id));
  }

  function doDelete() {
    const id = Number(docId);
    probe("DELETE", `/api/documents/${id}`, () => deleteDocument(token, id));
  }

  function doListUsers() {
    probe("GET", "/api/users", () => listUsers(token));
  }

  return (
    <div>
      <h2>Probador de la matriz</h2>
      <p className="note">
        Elegí el ID de un documento del seed y mandá las peticiones. Mirá el
        status vs. lo que dice la matriz (tu rol: <strong>{payload.role}</strong>,
        tenant: <strong>{payload.tenant_id}</strong>).
      </p>

      <div className="probe-row">
        <label>
          Doc ID
          <input
            className="mono"
            type="number"
            min={1}
            value={docId}
            onChange={(ev) => setDocId(ev.target.value)}
            style={{ width: 70 }}
          />
        </label>
        <div className="probe-buttons">
          <button className="btn small" onClick={doGet}>
            GET
          </button>
          <button className="btn small" onClick={doPatch}>
            PATCH
          </button>
          <button className="btn small" onClick={doPublish}>
            PUBLISH
          </button>
          <button className="btn small danger" onClick={doDelete}>
            DELETE
          </button>
          <span className="probe-sep" />
          <button className="btn small" onClick={doListUsers}>
            GET /users
          </button>
        </div>
      </div>

      {result && (
        <pre className={`code-block ${result.status >= 400 ? "err" : "ok"}`}>
          {`${result.method} ${result.path} → ${result.status}\n${JSON.stringify(result.body, null, 2)}`}
        </pre>
      )}

      <div className="probe-legend">
        <h3>Casos del seed (Acme)</h3>
        <table className="mini-table">
          <tbody>
            <tr><td>1</td><td>público Acme</td><td>todos → 200</td></tr>
            <tr><td>2</td><td>privado admin Acme</td><td>admin=200 · editor/viewer=403</td></tr>
            <tr><td>3</td><td>privado editor Acme</td><td>dueño=200 · admin=200 · otro=403</td></tr>
            <tr><td>4</td><td>público Acme</td><td>todos → 200</td></tr>
            <tr><td>5</td><td>privado Globex</td><td>cross-tenant → 403</td></tr>
            <tr><td>999</td><td>no existe</td><td>404</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
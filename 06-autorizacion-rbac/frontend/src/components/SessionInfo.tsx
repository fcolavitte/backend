import { scopeAllowsWrite } from "../authz";
import type { JwtPayload } from "../types";

interface Props {
  payload: JwtPayload;
  onLogout: () => void;
}

/**
 * El JWT decodificado SIN el secreto. La lección del módulo 05 sigue
 * viva: el payload es base64url, cualquier cliente lo lee. Por eso la
 * autorización NO confía ciegamente en estos claims:
 *
 *   - El ROL se relee del storage en CADA request (cambio inmediato).
 *     Si un admin te degrada, el claim de acá queda viejo pero el server
 *     ya te trata como viewer. Eso es lo que tu dependencies.py hace.
 *   - El SCOPE, en cambio, ES del token: lo fijó el login y lo respeta
 *     hasta que expire. "read write" = este token escribe; "read" = no.
 */
export default function SessionInfo({ payload, onLogout }: Props) {
  const readOnly = !scopeAllowsWrite(payload.scope);

  return (
    <div>
      <div className="section-title">
        <h2>Tu sesión — el JWT decodificado</h2>
        <button className="btn" onClick={onLogout}>
          Salir
        </button>
      </div>

      <table className="claims">
        <tbody>
          <tr>
            <td className="claim-key">sub (id usuario)</td>
            <td className="claim-val mono">{payload.sub}</td>
          </tr>
          <tr>
            <td className="claim-key">role</td>
            <td className="claim-val">
              <span className={`badge badge-${payload.role}`}>{payload.role}</span>
              <span className="hint">al momento del login</span>
            </td>
          </tr>
          <tr>
            <td className="claim-key">tenant_id</td>
            <td className="claim-val mono">{payload.tenant_id}</td>
          </tr>
          <tr>
            <td className="claim-key">scope</td>
            <td className="claim-val">
              <span className={`badge ${readOnly ? "badge-viewer" : "badge-editor"}`}>
                {payload.scope}
              </span>
              {readOnly && (
                <span className="hint warn">SOLO LECTURA: la UI y el server te frenan al escribir</span>
              )}
            </td>
          </tr>
          <tr>
            <td className="claim-key">exp (expira)</td>
            <td className="claim-val mono">{new Date(payload.exp * 1000).toLocaleString()}</td>
          </tr>
        </tbody>
      </table>

      <p className="note">
        💡 El server relee el <strong>rol</strong> de su storage en cada request; este claim
        es una foto del login. Pero el <strong>scope</strong> sí vive acá, en el token.
      </p>
    </div>
  );
}
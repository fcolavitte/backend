import { useState } from "react";
import { basicMe } from "../../api";
import type { ApiResult, UserRead } from "../../types";
import { AuthForm, PanelShell, ProfileCard, ResultBox } from "./shared";

/**
 * Método 1 — BASIC AUTH.
 *
 * No hay "login": las credenciales viajan en CADA request dentro del header
 * `Authorization: Basic base64(email:password)`. No hay logout del server:
 * el cliente solo deja de mandarlas.
 *
 * El panel calcula Y te muestra el header exacto que se manda. El botón
 * "decodificar" demuestra que base64 NO es cifrado: es codificación.
 */

export default function BasicPanel() {
  const [user, setUser] = useState<UserRead | null>(null);
  const [result, setResult] = useState<ApiResult<UserRead> | null>(null);
  const [busy, setBusy] = useState(false);
  const [decodedOpen, setDecodedOpen] = useState(false);
  const [lastToken, setLastToken] = useState<string>("");

  async function handleSubmit(email: string, password: string) {
    setBusy(true);
    const res = await basicMe(email, password);
    setResult(res);
    setUser(res.ok && res.data ? res.data : null);
    setLastToken(btoa(`${email}:${password}`));
    setDecodedOpen(false);
    setBusy(false);
  }

  return (
    <PanelShell
      numero="1"
      titulo="Basic Auth (RFC 7617)"
      leccion={
        <>
          Las credenciales van en el header <code>Authorization: Basic</code> en{" "}
          <strong>CADA request</strong>. Fijate que el panel te muestra el header
          exacto. Y ojo: <code>base64</code> es <em>codificación</em>, no cifrado.
          Hacé click en "decodificar" y ves el email y password en texto plano.
        </>
      }
    >
      <AuthForm onSubmit={handleSubmit} submitLabel="GET /api/me/basic" busy={busy} />

      {lastToken && (
        <div className="header-preview">
          <p>
            El header que viaja con cada request:{" "}
            <code className="wrap">Authorization: Basic {lastToken}</code>
          </p>
          <button onClick={() => setDecodedOpen((open) => !open)}>
            {decodedOpen ? "Ocultar" : "Decodificar (base64 ≠ cifrado)"}
          </button>
          {decodedOpen && (
            <p className="decoded">
              <strong>{atob(lastToken)}</strong> ← así ve un atacante tu
              password. Por eso Basic solo tiene sentido sobre HTTPS.
            </p>
          )}
        </div>
      )}

      <ResultBox result={result} />
      <ProfileCard user={user} />
    </PanelShell>
  );
}
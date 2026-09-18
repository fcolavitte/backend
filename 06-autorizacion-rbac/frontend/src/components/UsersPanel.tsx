import { useEffect, useState } from "react";
import { changeRole, listUsers } from "../api";
import { canChangeRole } from "../authz";
import type { Role, UserRead } from "../types";

interface Props {
  token: string;
  currentUserId: number;
  currentRole: Role;
}

/** Selector de rol inline por fila. */
function RoleSelect({
  value,
  onChange,
}: {
  value: Role;
  onChange: (r: Role) => void;
}) {
  return (
    <select value={value} onChange={(ev) => onChange(ev.target.value as Role)}>
      <option value="admin">admin</option>
      <option value="editor">editor</option>
      <option value="viewer">viewer</option>
    </select>
  );
}

/**
 * Panel de usuarios — visible solo para ADMIN (App.tsx ya lo filtra con
 * canManageUsers). Cambiar roles es "la operación más sensible del
 * sistema" (docstring del backend): con esto creás más admins o
 * degradás a alguien.
 *
 * Probalo: cambiate tu propio rol a viewer y mirá el SessionInfo — el
 * claim del token queda viejo, pero el server YA te trata como viewer
 * en el próximo request (la autorización relee storage). Ese es el
 * motivo por el que el rol no se lee del token.
 */
export default function UsersPanel({ token, currentUserId, currentRole }: Props) {
  const [users, setUsers] = useState<UserRead[]>([]);
  const [drafts, setDrafts] = useState<Record<number, Role>>({});
  const [message, setMessage] = useState<string | null>(null);

  function load() {
    void listUsers(token).then((res) => {
      if (res.ok && res.data) setUsers(res.data);
      else setMessage(`${res.status}: ${res.detail}`);
    });
  }

  useEffect(load, [token]);

  function applyRole(userId: number) {
    const role = drafts[userId];
    if (!role) return;
    void changeRole(token, userId, role).then((res) => {
      if (res.ok && res.data) {
        setMessage(
          `PATCH /api/users/${userId}/role → 200. Rol de ${res.data.email}: ${res.data.role}` +
            (userId === currentUserId
              ? " (¡te cambiaste TU rol! Mirá en SessionInfo cómo el claim quedó viejo)."
              : ""),
        );
        load();
      } else {
        setMessage(`${res.status}: ${res.detail}`);
      }
    });
  }

  return (
    <div>
      <div className="section-title">
        <h2>Usuarios de tu empresa</h2>
        <button className="btn" onClick={load}>
          Refrescar
        </button>
      </div>
      <p className="note">
        Solo admin puede ver/cambiar roles, y solo dentro de SU empresa
        (cross-tenant → 403). Completá <code>canChangeRole</code> en{" "}
        <code>authz.ts</code> para que esta UI respete la matriz.
      </p>

      {users.length === 0 ? (
        <p className="empty">Sin usuarios para mostrar.</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Email</th>
              <th>Rol</th>
              <th>Tenant</th>
              <th /> {/* acciones */}
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className={u.id === currentUserId ? "row-self" : ""}>
                <td className="mono">{u.id}</td>
                <td>
                  {u.name}
                  {u.id === currentUserId && <span className="tag">vos</span>}
                </td>
                <td className="mono">{u.email}</td>
                <td>
                  <span className={`badge badge-${u.role}`}>{u.role}</span>
                </td>
                <td>{u.tenant_id}</td>
                <td className="actions">
                  {canChangeRole(currentRole) ? (
                    <>
                      <RoleSelect
                        value={drafts[u.id] ?? u.role}
                        onChange={(r) => setDrafts((d) => ({ ...d, [u.id]: r }))}
                      />
                      <button className="btn small" onClick={() => applyRole(u.id)}>
                        Aplicar
                      </button>
                    </>
                  ) : (
                    <span className="hint">solo admin</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {message && <p className="info-line">{message}</p>}
    </div>
  );
}
import { useEffect, useState } from "react";
import {
  createDocument,
  deleteDocument,
  getDocument,
  listDocuments,
  publishDocument,
  updateDocument,
} from "../api";
import { canDelete, canEdit, canPublish, scopeAllowsWrite } from "../authz";
import type { DocumentPatch, DocumentRead, JwtPayload } from "../types";

interface Props {
  token: string;
  payload: JwtPayload;
}

/**
 * CRUD de documentos — el recurso protegido. Las acciones aparecen
 * según los helpers de authz.ts:
 *
 *   Crear / Editar / Publicar → scopeAllowsWrite + canEdit / canPublish
 *   Borrar → canDelete (admin) + scopeAllowsWrite
 *   Ver detalle → el server decide si podés (object-level + tenancy)
 *
 * 🔴 IDOR: la lección del módulo. Si el backend está roto, logueate
 *    como viewer y pedí GET /api/documents/5 (plan Globex) en el
 *    ProberPanel. Hoy da 200 (vulnerable). Cuando completes el backend,
 *    da 403 — la UI NO tiene que ofrecerte ver ese documento.
 *    Completá los helpers y la UI se alinea con el server.
 */
export default function DocumentsPanel({ token, payload }: Props) {
  const userId = Number(payload.sub);
  const [docs, setDocs] = useState<DocumentRead[]>([]);
  const [createTitle, setCreateTitle] = useState("");
  const [createContent, setCreateContent] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editContent, setEditContent] = useState("");
  const [editVisibility, setEditVisibility] = useState<"public" | "private">("private");
  const [detail, setDetail] = useState<{ doc: DocumentRead; status: number } | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const canWrite = scopeAllowsWrite(payload.scope);

  function load() {
    void listDocuments(token).then((res) => {
      if (res.ok && res.data) setDocs(res.data);
    });
  }

  useEffect(load, [token]);

  function handleCreate() {
    if (!createTitle.trim() || !createContent.trim()) return;
    void createDocument(token, createTitle, createContent).then((res) => {
      if (res.ok) {
        setMessage(`201 — "${res.data?.title}" creado (draft privado)`);
        setCreateTitle("");
        setCreateContent("");
        load();
      } else {
        setMessage(`${res.status}: ${res.detail}`);
      }
    });
  }

  function openEdit(doc: DocumentRead) {
    setEditingId(doc.id);
    setEditTitle(doc.title);
    setEditContent(doc.content);
    setEditVisibility(doc.visibility);
  }

  function handleEdit(id: number) {
    const patch: DocumentPatch = {};
    if (editTitle.trim()) patch.title = editTitle;
    if (editContent.trim()) patch.content = editContent;
    patch.visibility = editVisibility;
    void updateDocument(token, id, patch).then((res) => {
      if (res.ok) {
        setMessage(`PATCH → 200: "${res.data?.title}" editado`);
        setEditingId(null);
        load();
      } else {
        setMessage(`${res.status}: ${res.detail}`);
      }
    });
  }

  function handlePublish(id: number) {
    void publishDocument(token, id).then((res) => {
      if (res.ok) {
        setMessage(`POST → 200: "${res.data?.title}" publicado`);
        load();
      } else {
        setMessage(`${res.status}: ${res.detail}`);
      }
    });
  }

  function handleDelete(id: number) {
    void deleteDocument(token, id).then((res) => {
      if (res.ok) {
        setMessage(`DELETE → 200: "${res.data?.title}" borrado`);
        load();
      } else {
        setMessage(`${res.status}: ${res.detail}`);
      }
    });
  }

  function viewDetail(id: number) {
    setDetail(null);
    void getDocument(token, id).then((res) => {
      setDetail({
        doc: { ...(res.data ?? { id, owner_id: 0, tenant_id: 0, title: "-", content: "-", visibility: "private" as const, published: false, created_at: "" }) },
        status: res.status,
      });
      if (res.ok) {
        setMessage(`GET → 200: "${res.data?.title}"`);
      } else {
        setMessage(`GET → ${res.status}: ${res.detail}`);
      }
    });
  }

  return (
    <div>
      <div className="section-title">
        <h2>Documentos</h2>
        <span className="note inline">
          Públicos de tu empresa + los tuyos. Acciones según authz.ts.
        </span>
      </div>

      {canWrite && (
        <form
          className="create-form"
          onSubmit={(ev) => {
            ev.preventDefault();
            handleCreate();
          }}
        >
          <input
            placeholder="Título"
            value={createTitle}
            onChange={(ev) => setCreateTitle(ev.target.value)}
            required
          />
          <input
            placeholder="Contenido"
            value={createContent}
            onChange={(ev) => setCreateContent(ev.target.value)}
            required
          />
          <button className="btn primary" type="submit">
            Crear draft privado
          </button>
        </form>
      )}

      {!canWrite && (
        <p className="warn-line">
          ⚠️ Tu token tiene scope <strong>{payload.scope}</strong> (read) →
          la creación está bloqueada en la UI (server también responde 403).
        </p>
      )}

      <table className="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Título</th>
            <th>Visibilidad</th>
            <th>Publicado</th>
            <th>Dueño</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {docs.map((doc) => (
            <tr key={doc.id}>
              <td className="mono">{doc.id}</td>
              <td>
                {editingId === doc.id ? (
                  <input
                    className="inline-input"
                    value={editTitle}
                    onChange={(ev) => setEditTitle(ev.target.value)}
                  />
                ) : (
                  doc.title
                )}
              </td>
              <td>
                {editingId === doc.id ? (
                  <select
                    value={editVisibility}
                    onChange={(ev) =>
                      setEditVisibility(ev.target.value as "public" | "private")
                    }
                  >
                    <option value="private">privado</option>
                    <option value="public">público</option>
                  </select>
                ) : (
                  <span className={`badge badge-${doc.visibility === "public" ? "editor" : "viewer"}`}>
                    {doc.visibility}
                  </span>
                )}
              </td>
              <td>
                <span className={`badge badge-${doc.published ? "admin" : ""}`}>
                  {doc.published ? "sí" : "no"}
                </span>
              </td>
              <td className="mono">{doc.owner_id}</td>
              <td className="actions">
                <button className="btn small" onClick={() => viewDetail(doc.id)}>
                  Ver
                </button>
                {editingId === doc.id ? (
                  <>
                    <button className="btn small primary" onClick={() => handleEdit(doc.id)}>
                      Guardar
                    </button>
                    <button className="btn small" onClick={() => setEditingId(null)}>
                      Cancelar
                    </button>
                  </>
                ) : (
                  <>
                    {canEdit(userId, doc, payload.role) && canWrite && (
                      <button className="btn small" onClick={() => openEdit(doc)}>
                        Editar
                      </button>
                    )}
                    {canPublish(userId, doc, payload.role) && canWrite && !doc.published && (
                      <button className="btn small" onClick={() => handlePublish(doc.id)}>
                        Publicar
                      </button>
                    )}
                    {canDelete(payload.role) && canWrite && (
                      <button className="btn small danger" onClick={() => handleDelete(doc.id)}>
                        Borrar
                      </button>
                    )}
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {detail && (
        <pre className={`code-block ${detail.status >= 400 ? "err" : "ok"}`}>
          {`GET /api/documents → ${detail.status}\n${JSON.stringify(detail.doc, null, 2)}`}
        </pre>
      )}

      {message && <p className="info-line">{message}</p>}
    </div>
  );
}
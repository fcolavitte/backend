"""
Controller de DOCUMENTOS — el recurso protegido (object-level + scopes).

┌─────────────────────────────────────────────────────────────────────────┐
│ 🔓 COMPLETÁS VOS: ESTE es el archivo más importante de la entrega.     │
│                                                                         │
│   POST   /api/documents            → crear     (scope "write")          │
│   GET    /api/documents            → listar    (públicos + los tuyos)   │
│   GET    /api/documents/{id}       → ver       (dueño / admin / público)│
│   PATCH  /api/documents/{id}       → editar    (dueño o admin, "write") │
│   DELETE /api/documents/{id}       → borrar    (admin, "write")         │
│   POST   /api/documents/{id}/publish → publicar (dueño o admin, "write")│
│                                                                         │
│ 🔴 El estado actual es el ATACANTE A01 del OWASP: **IDOR**.             │
│    Cualquier autenticado que conozca el id lee/edita/borra TODO.        │
│    Probalo: logueate como viewer@acme.com y pedí GET /api/documents/5   │
│    (el plan secreto de Globex) → responde 200. LUSTRADA.                │
│                                                                         │
│ ✅ TU TRABAJO, en cada endpoint:                                        │
│    1. SCOPE: los que modifican datos exigen Depends(require_scope("write"))│
│    2. TENANCY: si document.tenant_id != current_user.tenant_id → 403   │
│       (aplica SIEMPRE, incluso para documentos públicos)               │
│    3. OBJECT-LEVEL: si es privado → solo dueño (owner_id == tu id) o    │
│       admin del tenant. Si no → 403.                                   │
│    4. ROL: DELETE exige admin (matriz) — el resto de los GRISES salen  │
│       del scope: viewer tiene scope "read" → ya no llega a crear.      │
│                                                                         │
│ 🧠 Pregunta para la defensa: ¿por qué acá el 403 va DESPUÉS del 404?   │
│    (si un id no existe, no hay nada que proteger — pero en producción  │
│    algunos devuelven 404 también en cross-tenant para no filtrar       │
│    existencia. Acá usamos 403 para que la lección sea VISIBLE).        │
└─────────────────────────────────────────────────────────────────────────┘
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app import storage
from app.dependencies import get_current_user, require_role, require_scope
from app.models import DocumentCreate, DocumentRead, DocumentUpdate, Role, User

router = APIRouter(prefix="/api", tags=["3 · Documentos"])


@router.post(
    "/documents",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    body: DocumentCreate,
    current_user: User = Depends(get_current_user),  # 🔓 TODO: Depends(require_scope("write"))
):
    """Crea un documento: draft privado a nombre tuyo, en TU empresa.

    El documento nace como borrador del autor; publicarlo es otra operación.
    """
    return storage.create_document(owner=current_user, body=body)


@router.get("/documents", response_model=list[DocumentRead])
def list_documents(
    current_user: User = Depends(get_current_user),
):
    """Lista lo que PODÉS ver: públicos de tu empresa + tus documentos.

    El filtro ya lo hace storage.list_documents(tenant_id, user_id) — el
    tenancy acá es del STORAGE. Este endpoint es de lectura: scope "read"
    alcanza (y el default de todos los roles incluye "read").
    """
    return storage.list_documents(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
    )


@router.get("/documents/{doc_id}", response_model=DocumentRead)
def get_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
):
    """Ve un documento por id. 🔴 ACÁ VIVE EL IDOR: el caso más violado.

    Reglas que tenés que implementar en orden:
        1. 404 si el documento no existe.
        2. 🔓 TENANCY: si doc.tenant_id != current_user.tenant_id → 403.
           (documento de OTRA empresa: 403 para TODOS, incluso admin).
        3. Si visibility == "public" → devolvelo (todos lo ven).
        4. 🔓 OBJECT-LEVEL: si es PRIVADO → ¿sos el dueño
           (doc.owner_id == current_user.id) o admin de la empresa?
           NO → 403. SÍ → devolvelo.
    """
    doc = storage.get_document(doc_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")
    # 🔓 TU CÓDIGO ACÁ (tenancy + object-level según las reglas de arriba).
    return doc


@router.patch("/documents/{doc_id}", response_model=DocumentRead)
def update_document(
    doc_id: int,
    body: DocumentUpdate,
    current_user: User = Depends(get_current_user),  # 🔓 TODO: Depends(require_scope("write"))
):
    """Edita un documento: solo el DUEÑO o un ADMIN de la empresa."""
    doc = storage.get_document(doc_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")
    # 🔓 TODO: tenancy (403 si es de otra empresa).
    # 🔓 TODO: object-level — ¿dueño o admin? si NO → 403 ("No podés editar este documento").
    return storage.update_document(doc_id, body)


@router.delete("/documents/{doc_id}", response_model=DocumentRead)
def delete_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),  # 🔓 TODO: Depends(require_role(Role.ADMIN)) + Depends(require_scope("write"))
):
    """Borra un documento: SOLO admin (la matriz exige 403 para editor/viewer)."""
    doc = storage.get_document(doc_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")
    # 🔓 TODO: tenancy — un admin de Acme no borra docs de Globex (403).
    deleted = storage.delete_document(doc_id)
    return deleted


@router.post("/documents/{doc_id}/publish", response_model=DocumentRead)
def publish_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),  # 🔓 TODO: Depends(require_scope("write"))
):
    """Publica un documento: el DUEÑO publica lo suyo; el admin, cualquiera.

    La matriz exige: admin ✅ · editor ✅ (lo suyo) · viewer ❌403.
    El viewer ya queda afuera por su scope "read" — vos solo tenés que
    aplicar dueño-o-admin + tenancy.
    """
    doc = storage.get_document(doc_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")
    # 🔓 TODO: tenancy (403 si es de otra empresa).
    # 🔓 TODO: object-level — ¿dueño o admin? si NO → 403 ("No podés publicar este documento").
    return storage.set_document_published(doc_id, True)
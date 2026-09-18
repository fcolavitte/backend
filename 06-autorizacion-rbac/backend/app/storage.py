"""
Persistencia REAL — usuarios, roles y documentos en PostgreSQL (SQLModel).

Antes (módulos anteriores): dicts en memoria → TODO se borraba al apagar.
Ahora: cada usuario autenticado y cada rol autorizado viven en la base de
datos y PERSISTEN entre reinicios (volumen docker `pgdata`).

Este archivo conserva las MISMAS firmas de siempre — los controllers y las
dependencias de autorización no cambiaron. Lo que cambió es el cuerpo:
dicts → sesiones SQLAlchemy. El alumno sigue completando SOLO los 4
archivos 🔓; acá no se toca nada en la entrega.

EL SEED es IDEMPOTENTE: siembra el dataset demo (2 tenants, 4 usuarios,
5 documentos) SOLO si la tabla de usuarios está vacía. Si la DB ya tiene
datos (porque el script de verificación ya corrió, o porque reiniciaste),
NO duplica nada.

  Tenant 1 · Acme Corp              Tenant 2 · Globex Inc
    admin@acme.com   (admin)          admin@globex.com (admin)
    editor@acme.com  (editor)
    viewer@acme.com  (viewer)

  Documentos:
    #1 "Manual de bienvenida"  público, publicado   (owner: admin acme)
    #2 "Estrategia 2026"       privado, draft        (owner: admin acme)
    #3 "Notas de reunión"      privado, draft        (owner: editor acme)
    #4 "Informe público Q3"    público, publicado    (owner: editor acme)
    #5 "Plan secreto Globex"   privado, draft        (owner: admin globex)

  Password de TODOS los usuarios demo: demo12345
"""

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app import db, security
from app.config import DEFAULT_TENANT_ID, DEMO_PASSWORD
from app.models import Document, DocumentCreate, DocumentUpdate, Role, User, UserCreate


# ── Mapeo tablas ←→ modelos Pydantic (frontera entre DB y API) ─────────────


def _to_user(row: db.UserDB) -> User:
    return User(
        id=row.id,
        email=row.email,
        name=row.name,
        password_hash=row.password_hash,
        role=Role(row.role),
        tenant_id=row.tenant_id,
        created_at=row.created_at,
    )


def _to_document(row: db.DocumentDB) -> Document:
    return Document(
        id=row.id,
        owner_id=row.owner_id,
        tenant_id=row.tenant_id,
        title=row.title,
        content=row.content,
        visibility=row.visibility,
        published=row.published,
        created_at=row.created_at,
    )


# ── Seed (idempotente + auto-reparador) ────────────────────────────────────


def seed() -> None:
    """Garantiza el dataset demo en CADA arranque (seed auto-reparador).

    Los fixtures demo tienen IDs FIJOS (tenants 1..2, users 1..4, docs 1..5):
    la spec y el script de verificación los referencian por id ("documento
    #1", "id 4 = admin de Globex"). Con postgres SERIAL un re-insert cambiaría
    el id — por eso la semilla lo fija explicitamente.

    Por qué "auto-reparador": mientras los archivos 🔓 no estén completos, el
    script de verificación puede BORRAR documentos demo (un check que espera
    403 y recibe 200 ejecuta el DELETE igual). Con memoria eso se re-sembraba
    solo; con persistencia habría que reparar a mano. Acá: si un fixture falta
    (lo borraron en alguna corrida), este seed lo re-crea al reiniciar.

    Los registros del ALUMNO (register, documentos nuevos del script) NO se
    tocan jamás: persisten entre reinicios. El seed solo garantiza fixtures.
    """
    db.create_db_and_tables()
    _seed_tenants()
    _seed_users()
    _seed_documents()
    _reset_sequences()


def _seed_tenants() -> None:
    with Session(db.engine) as session:
        for tid, name in ((1, "Acme Corp"), (2, "Globex Inc")):
            if session.get(db.TenantDB, tid) is None:
                session.add(db.TenantDB(id=tid, name=name))
        session.commit()


def _seed_users() -> None:
    rows = (
        (1, "admin@acme.com", "Admin Acme", Role.ADMIN, 1),
        (2, "editor@acme.com", "Editor Acme", Role.EDITOR, 1),
        (3, "viewer@acme.com", "Viewer Acme", Role.VIEWER, 1),
        (4, "admin@globex.com", "Admin Globex", Role.ADMIN, 2),
    )
    with Session(db.engine) as session:
        for uid, email, name, role, tenant_id in rows:
            if session.get(db.UserDB, uid) is None:
                session.add(db.UserDB(
                    id=uid,
                    email=email,
                    name=name,
                    password_hash=security.hash_password(DEMO_PASSWORD),
                    role=role.value,
                    tenant_id=tenant_id,
                ))
        session.commit()


def _seed_documents() -> None:
    rows = (
        (1, "Manual de bienvenida", "Cómo configurar tu cuenta y tus herramientas.", 1, 1, "public", True),
        (2, "Estrategia 2026", "Objetivos anuales y presupuesto. CONFIDENCIAL.", 1, 1, "private", False),
        (3, "Notas de reunión", "Acciones acordadas con el equipo de marketing.", 2, 1, "private", False),
        (4, "Informe público Q3", "Resultados del trimestre, versión para clientes.", 2, 1, "public", True),
        (5, "Plan secreto Globex", "Lanzamiento sorpresa. NO debe verlo Acme.", 4, 2, "private", False),
    )
    with Session(db.engine) as session:
        for did, title, content, owner_id, tenant_id, visibility, published in rows:
            if session.get(db.DocumentDB, did) is None:
                session.add(db.DocumentDB(
                    id=did,
                    owner_id=owner_id,
                    tenant_id=tenant_id,
                    title=title,
                    content=content,
                    visibility=visibility,
                    published=published,
                ))
        session.commit()


def _reset_sequences() -> None:
    """Tras insertar con ids fijos, alinea el SERIAL: el próximo insert (los
    registros del alumno) sigue la numeración sin chocar con los fixtures."""
    with Session(db.engine) as session:
        for table in ("tenants", "users", "documents"):
            session.execute(text(
                f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                f"COALESCE((SELECT MAX(id) FROM {table}), 1))"
            ))
        session.commit()


# ── Usuarios ───────────────────────────────────────────────────────────────


def create_user(body: UserCreate, role: Role = Role.VIEWER, tenant_id: int | None = None) -> User | None:
    """Crea un usuario PERSISTIDO. Devuelve None si el email ya existe.

    Un usuario nuevo SIEMPRE nace como viewer (regla de negocio): el rol lo
    asigna un admin después con PATCH /api/users/{id}/role.
    """
    email = body.email.lower().strip()
    with Session(db.engine) as session:
        row = db.UserDB(
            email=email,
            name=body.name,
            password_hash=security.hash_password(body.password),
            role=role.value,
            tenant_id=tenant_id or DEFAULT_TENANT_ID,
        )
        session.add(row)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            return None
        session.refresh(row)
        return _to_user(row)


def get_user_by_email(email: str) -> User | None:
    with Session(db.engine) as session:
        row = session.exec(
            select(db.UserDB).where(db.UserDB.email == email.lower().strip())
        ).first()
        return _to_user(row) if row else None


def get_user_by_id(user_id: int) -> User | None:
    with Session(db.engine) as session:
        row = session.get(db.UserDB, user_id)
        return _to_user(row) if row else None


def list_users(tenant_id: int) -> list[User]:
    """TODOS los usuarios de UNA empresa. La regla de tenancy se aplica ACÁ:
    nunca se devuelve un usuario de otra empresa. El que llama ya autorizó."""
    with Session(db.engine) as session:
        rows = session.exec(
            select(db.UserDB).where(db.UserDB.tenant_id == tenant_id)
        ).all()
        return [_to_user(r) for r in rows]


def set_user_role(user_id: int, role: Role) -> User | None:
    """Cambia el rol de un usuario (PERSISTE el cambio). None si no existe."""
    with Session(db.engine) as session:
        row = session.get(db.UserDB, user_id)
        if row is None:
            return None
        row.role = role.value
        session.add(row)
        session.commit()
        session.refresh(row)
        return _to_user(row)


def user_count() -> int:
    with Session(db.engine) as session:
        return len(session.exec(select(db.UserDB)).all())


# ── Documentos ─────────────────────────────────────────────────────────────


def create_document(
    owner: User,
    body: DocumentCreate,
    visibility: str = "private",
    published: bool = False,
) -> Document:
    """Crea un documento a nombre del owner, en el tenant del owner.

    El tenant_id NO viene del body: viene del usuario autenticado. Un usuario
    de Acme no puede crear documentos de Globex ni a palos (no hay forma de
    pedirlo).
    """
    with Session(db.engine) as session:
        row = db.DocumentDB(
            owner_id=owner.id,
            tenant_id=owner.tenant_id,
            title=body.title,
            content=body.content,
            visibility=visibility,
            published=published,
        )
        session.add(row)
        session.commit()
        session.refresh(row)
        return _to_document(row)


def get_document(doc_id: int) -> Document | None:
    with Session(db.engine) as session:
        row = session.get(db.DocumentDB, doc_id)
        return _to_document(row) if row else None


def list_documents(tenant_id: int, user_id: int) -> list[Document]:
    """Lo que un usuario PUEDE ver dentro de su empresa:
    - documentos públicos del tenant, +
    - los documentos propios (cualquier visibilidad/estado).
    Los documentos de OTRA empresa jamás aparecen acá (tenancy en el storage).
    """
    with Session(db.engine) as session:
        rows = session.exec(
            select(db.DocumentDB).where(
                db.DocumentDB.tenant_id == tenant_id,
                (db.DocumentDB.visibility == "public") | (db.DocumentDB.owner_id == user_id),
            )
        ).all()
        return [_to_document(r) for r in rows]


def update_document(doc_id: int, body: DocumentUpdate) -> Document | None:
    """Aplica los campos presentes del body (y PERSISTE). None si no existe."""
    with Session(db.engine) as session:
        row = session.get(db.DocumentDB, doc_id)
        if row is None:
            return None
        if body.title is not None:
            row.title = body.title
        if body.content is not None:
            row.content = body.content
        if body.visibility is not None:
            row.visibility = body.visibility
        session.add(row)
        session.commit()
        session.refresh(row)
        return _to_document(row)


def set_document_published(doc_id: int, published: bool) -> Document | None:
    """Publica (o despublica) un documento. None si no existe."""
    with Session(db.engine) as session:
        row = session.get(db.DocumentDB, doc_id)
        if row is None:
            return None
        row.published = published
        session.add(row)
        session.commit()
        session.refresh(row)
        return _to_document(row)


def delete_document(doc_id: int) -> Document | None:
    """Borra un documento PERSISTIDO. None si no existe."""
    with Session(db.engine) as session:
        row = session.get(db.DocumentDB, doc_id)
        if row is None:
            return None
        session.delete(row)
        session.commit()
        return _to_document(row)


def document_count() -> int:
    with Session(db.engine) as session:
        return len(session.exec(select(db.DocumentDB)).all())


def tenant_count() -> int:
    with Session(db.engine) as session:
        return len(session.exec(select(db.TenantDB)).all())
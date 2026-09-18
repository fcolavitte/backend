# ──────────────────────────────────────────────────────────────────────────
# Módulo 06 — Autorización RBAC · Imagen del backend (FastAPI)
#
# La app persiste en PostgreSQL (service `postgres` del compose): el seed
# siembra el dataset demo SOLO la primera vez (idempotente). Sin base de
# datos no arranca — el compose espera el healthcheck de postgres primero.
# El entrypoint usa uvicorn con --host 0.0.0.0 para que el contenedor sea
# alcanzable desde el host (y desde el frontend en la red de Compose).
#
# TOOLCHAIN: usa uv — la MISMA herramienta del desarrollo local
# (uv sync / uv run). El binario se copia desde la imagen oficial de
# astral-sh (no se instala con pip). uv.lock congela las versiones exactas:
# lo que corre acá es idéntico a lo que corre en tu máquina con `uv sync`.
#
# No toqués este archivo en la entrega: es infraestructura de la cátedra.
# ──────────────────────────────────────────────────────────────────────────

FROM python:3.12-slim

# uv: la misma toolchain del dev local (versión fija → build reproducible)
COPY --from=ghcr.io/astral-sh/uv:0.10.2 /uv /uv/bin/uv
ENV PATH="/uv/bin:$PATH"

WORKDIR /app

# 1) Dependencias primero (capa cacheable): lockfile congelado, sin el código.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# 2) El código del paquete `app` (hatchling) después — solo esta capa cambia.
COPY app ./app
RUN uv sync --frozen

EXPOSE 8000

# host 0.0.0.0: dentro del contenedor el service no vive en "localhost" del host.
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
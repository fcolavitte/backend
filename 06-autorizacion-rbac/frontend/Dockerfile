# ──────────────────────────────────────────────────────────────────────────
# Módulo 06 — Autorización RBAC · Imagen del frontend (React + Vite)
#
# La herramienta visual de prueba. Corre Vite DEV con --host 0.0.0.0 para ser
# alcanzable desde el host. El proxy hacia la API se configura con la
# variable VITE_PROXY_TARGET (la define docker-compose.yml → backend:8000).
#
# TOOLCHAIN: pnpm vía corepack (incluido en Node) — la MISMA herramienta
# del desarrollo local. La versión exacta la declara el campo
# "packageManager" de package.json, así que lo que corre acá es idéntico
# a lo que corre en tu máquina con `pnpm install`. No se usa npm.
#
# No toqués este archivo en la entrega: es infraestructura de la cátedra.
# ──────────────────────────────────────────────────────────────────────────

FROM node:22-alpine

WORKDIR /app

# corepack activa pnpm usando la versión de packageManager (sin prompts).
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0
RUN corepack enable

# Dependencias primero (capa cacheable): lockfile congelado → build reproducible.
# pnpm-workspace.yaml trae la config de builds aprobados (esbuild, pnpm 10+).
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .

EXPOSE 5173

# --host 0.0.0.0: dentro del contenedor, escuchar en todas las interfaces.
CMD ["pnpm", "dev", "--host", "0.0.0.0"]
# Build context: repo root (docker build -f frontend-react/Dockerfile .)
FROM node:22-slim AS build

WORKDIR /app
COPY frontend-react/package.json frontend-react/package-lock.json* ./
RUN npm ci

COPY frontend-react/ .
# VITE_API_URL is baked into the static bundle at build time (Vite env vars are compile-time,
# not runtime). Left unset here on purpose: src/lib/api.ts falls back to "" (same-origin,
# relative requests) when it's unset, and Caddy reverse-proxies the backend's own route
# prefixes to the backend container (see deploy/Caddyfile) -- no CORS hop needed in production.
# Override with --build-arg VITE_API_URL=https://api.example.com only if the backend is ever
# split onto a different host.
ARG VITE_API_URL=
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# --- serve stage: Caddy serves the static build and reverse-proxies /api/* to the backend ---
FROM caddy:2-alpine

COPY --from=build /app/dist /usr/share/caddy
COPY deploy/Caddyfile /etc/caddy/Caddyfile

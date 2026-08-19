# Error monitoring

Real-time alerting on unhandled errors, via [Sentry](https://sentry.io) -- backend and frontend
each report independently, both off by default (see `.env.example` /
`frontend-react/.env.example`), following the same "off unless explicitly configured" rule every
other optional integration in this project uses (LangSmith tracing, Sarvam itself).

Without this, an error in production is only visible if someone happens to be reading server
logs, or a citizen reports it. With it, an alert (email, Slack, whatever Sentry's own project
settings are pointed at) fires the moment something actually breaks.

## What's wired up

- **Backend** (`backend/main.py`'s `init_error_monitoring()`): every unhandled exception in any
  route is automatically captured and sent, with the FastAPI/Starlette route name attached.
- **Frontend** (`frontend-react/src/main.tsx`): a top-level `Sentry.ErrorBoundary` wraps the
  whole app. Two independent things happen on a crash:
  1. The error is reported to Sentry (only if `VITE_SENTRY_DSN` is set).
  2. The citizen sees a plain "Something went wrong / Reload page" screen instead of a blank
     white page. This part always happens, DSN or not -- a crash-safety net and an alerting
     integration are two different concerns that happen to share one component.

## Getting a DSN

1. Create a free account/project at [sentry.io](https://sentry.io) (or point at a self-hosted
   instance) -- one project for the backend (platform: Python/FastAPI), one for the frontend
   (platform: React), or one shared project for both.
2. Each project's Settings > Client Keys (DSN) page has the DSN string to copy.

## Turning it on

| Where | What to set | Effect |
|---|---|---|
| Server's `.env` (never committed, see `docker-compose.prod.yml`'s `env_file`) | `SENTRY_DSN`, `SENTRY_ENVIRONMENT=production` | Backend reporting -- read at container **startup**, so a plain restart picks up a newly-added DSN, no rebuild needed. |
| GitHub repo Settings > Secrets and variables > Actions | `VITE_SENTRY_DSN` | Frontend reporting -- Vite env vars are baked into the JS bundle at **build** time (see `frontend-react/Dockerfile`), so this must be a CI secret, not just a server `.env` entry; `.github/workflows/cd.yml` threads it through as a Docker build-arg. Takes effect on the next deploy after the secret is added. |
| Local dev (`.env` / `frontend-react/.env`) | Same variables | Same effect, immediately, for local testing -- see `SENTRY_ENVIRONMENT=development` default so local errors never mix into the production project's event stream. |

Leaving any of these unset is a fully supported, intentional state -- the app runs identically
either way, just without alerting.

## PII

`send_default_pii` / `sendDefaultPii` are explicitly set `false` on both sides (already the SDK
default; set explicitly so a future SDK version can't silently change it unnoticed). Complaint
text and phone numbers are real citizen PII this app handles -- error reports should contain
enough to diagnose *what broke*, not a copy of what the citizen typed.

## Performance tracing

`SENTRY_TRACES_SAMPLE_RATE` / `VITE_SENTRY_TRACES_SAMPLE_RATE` default to `0` -- this feature is
scoped to error alerting, not request profiling. Raise it (e.g. `0.1` for 10% of requests) only
if performance tracing is specifically wanted later; it's a separate, additional cost on Sentry's
hosted tiers.

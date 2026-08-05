# Future Work

Ideas and requirements that are explicitly out of scope for Milestone 1.
Nothing in this file should be implemented until its milestone arrives.

## Milestone 2 — Intelligent Product

- ~~JWT auth, real user/worker roles~~ — done: `backend/routes/auth.py`,
  `backend/routes/admin.py`, `backend/deps.py`. Citizens self-register;
  workers are created by a Super Admin; the first Super Admin is seeded via
  `scripts/seed_admin.py`, never through any API.
- ~~Better UI (React rebuild)~~ — done: `frontend-react/`, replacing the
  Streamlit apps in `frontend/` (kept for reference, now unauthenticated
  and out of sync with the backend's auth requirement).
- ~~Playwright integration tests~~ — done for auth/role flows: language
  gate → signup/login → role-scoped dashboards, worker creation, protected
  routes. See "Fast follow" below for what's still mocked or missing.
- PostgreSQL (replace SQLite)
- Vision analysis of complaint photos
- Category detection, priority detection, structured JSON output from the LLM
- Retry logic and smarter error recovery for AI calls
- Live status updates (polling/websockets), maps
- Accept / reject / reassignment workflow for workers
- Ward assignment for citizens (currently a free-text field per complaint,
  not tied to an address/geography)
- Password reset flow, phone number verification (OTP), rate limiting on
  login/signup

### Fast follow on the React rebuild specifically

- Voice input (STT) isn't wired into the citizen complaint form yet — text
  only for now, though the backend already supports audio uploads
- A couple of native browser controls (file input, language `<select>`)
  aren't custom-styled to match the rest of the design yet
- Playwright coverage for a *successful* complaint submission (translated,
  summarized, appears in a worker's queue) needs either a real
  `SARVAM_API_KEY` in the test environment or a backend test-mode that
  swaps in a mocked `ComplaintAgent` — today's e2e tests correctly assert
  the graceful-failure path instead, since no key is configured here

## Milestone 3 — Production Product

- LangGraph multi-agent orchestration
- Tool calling, Redis, async queues
- Docker, AWS deployment
- Prometheus, Grafana, OpenTelemetry, Alertmanager
- Centralized logging, CI/CD

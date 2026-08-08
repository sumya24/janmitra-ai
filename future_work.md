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
  (see `docs/AI_AGENT.md §6` for a scoped-out sketch of this as an agentic
  next step, reusing the existing pipeline)
- ~~Retry logic and smarter error recovery for AI calls~~ — partially done:
  voice complaints retry a failed speech-to-text chunk once before falling
  back to an explicit gap marker (`ComplaintAgent._transcribe_chunks`); text
  cleanup/summarization use a different strategy (best-effort fallback
  instead of retry, since their failures aren't reliably transient — see
  `docs/AI_AGENT.md §4`). Sarvam translation calls still have no retry.
- Live status updates (polling/websockets), maps — partially done: the
  citizen dashboard short-polls for status changes every 8s while anything
  is still in flight; no websockets/SSE yet, and no maps.
- ~~Accept / reject / reassignment workflow for workers~~ — done:
  `backend/services/assignment_service.py`, full pending → assigned →
  accepted → resolved lifecycle with automatic reassignment to the next
  eligible worker in the ward on rejection. See `docs/PROJECT_OVERVIEW.md §4`.
- ~~Ward assignment for citizens (currently a free-text field per complaint,
  not tied to an address/geography)~~ — done: a dropdown backed by
  `GET /complaints/wards` (real wards that actually have a worker), falling
  back to free text only if no wards are set up yet. Still not tied to a
  real address/geography lookup.
- Password reset flow, phone number verification (OTP), rate limiting on
  login/signup

### Fast follow on the React rebuild specifically

- ~~Voice input (STT) isn't wired into the citizen complaint form~~ — done:
  a Type/Speak toggle in `CitizenDashboard.tsx` records a voice note via the
  browser `MediaRecorder` API (`lib/useAudioRecorder.ts`) and uploads it on
  the existing `audio` field, with inline errors for a denied/missing mic.
- ~~Manual theme (light/dark) switcher~~ — done: `lib/theme.tsx` +
  `components/ThemeToggle.tsx`, a System → Light → Dark cycle persisted to
  localStorage, surfaced on the landing nav, login/signup, and every
  dashboard's top bar.
- A couple of native browser controls (file input, language `<select>`)
  aren't custom-styled to match the rest of the design yet
- ~~Playwright coverage for a *successful* complaint submission~~ — done:
  `e2e/complaint-tracking.spec.ts` runs the full lifecycle (real AI
  submission → assign → reject → reassign → accept → resolve → feedback)
  against a real `SARVAM_API_KEY`, ~20s for the AI call alone.

## Milestone 3 — Production Product

- LangGraph multi-agent orchestration
- Tool calling, Redis, async queues
- Docker, AWS deployment
- Prometheus, Grafana, OpenTelemetry, Alertmanager
- Centralized logging, CI/CD

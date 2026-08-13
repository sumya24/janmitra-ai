# JanSarthi AI — React Frontend

The React/TypeScript rebuild of JanSarthi AI's frontend, replacing the Streamlit
apps in `../frontend/`. Built on the design explored in the earlier UI mockup,
now wired to the real, authenticated backend.

## What's here

- A language gate (Marathi/Hindi/English) shown before anything else
- A public landing page, with Log in / Sign up in the corner
- Sign-up (citizen accounts only — see below) and login
- Citizen dashboard: submit a complaint by typing or recording your voice,
  view your own complaints
- Worker dashboard: view your ward's queue, mark complaints resolved
- Super Admin dashboard: create worker accounts, see workload per worker
- A Settings panel (change your name / preferred language, log out)
- A theme toggle (System / Light / Dark) on the landing nav, login/signup,
  and every dashboard's top bar — persisted to `localStorage`

**On roles:** there is no role picker anywhere in this app, on purpose.
Sign-up always creates a citizen account. Worker accounts can only be
created by a Super Admin, from the Admin dashboard. The first Super Admin
account isn't created through this app at all — see
`../scripts/seed_admin.py`, which seeds one directly into the database, the
way a real deployment would.

## Setup

```bash
npm install
cp .env.example .env   # VITE_API_URL, defaults to http://localhost:8000
npm run dev
```

The FastAPI backend must be running separately (see the repo root README).

## Testing

End-to-end tests run against a real backend + a real running dev server —
they're not mocked, so both need to be up first:

```bash
# terminal 1, from the repo root
python3 -m uvicorn backend.main:app --reload

# terminal 2, from here
npm run dev

# terminal 3, from here
npm run test:e2e
```

Note: complaint submission itself will fail gracefully in these tests
unless a real `SARVAM_API_KEY` is configured on the backend — the tests
that cover it assert the graceful-error path, not a real AI response.

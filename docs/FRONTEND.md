# The Frontend — React, from the Ground Up

*Written for someone who wants to actually understand this, not just skim it — including "why did you build it this way" answers you could give in an interview.*

> Part of the JanSarthi AI documentation set. See [`README.md`](../README.md) for the full index of every document.

---

## 1. What React actually is, and the problem it solves

Before frameworks like React, updating a web page after something changed (a new complaint arrives, a status changes) usually meant manually finding the right HTML element and mutating it (`document.getElementById(...).innerText = ...`) — code that gets tangled and error-prone fast as a page grows.

**React's core idea:** you describe *what the UI should look like for the current data*, as a function of that data, and React figures out the minimal set of real DOM changes needed to make the actual page match. You write `<div>{complaint.summary}</div>`; when `complaint.summary` changes, you don't touch the DOM yourself at all — you just describe the new desired state, and React handles updating the page.

This codebase's frontend lives entirely under [`frontend-react/src/`](../frontend-react/src/), written in **React + TypeScript**, built with **Vite**.

---

## 2. Why React, Vite, and TypeScript specifically

**Why React over alternatives (Vue, Angular, Svelte, or no framework):** React was chosen mainly for being the most widely known and hired-for option, with the largest ecosystem of libraries and the most available documentation/examples for a specific need. Vue and Svelte are legitimate, often simpler alternatives; Angular is a much heavier, more opinionated full framework better suited to very large teams/apps. For a project this size, the honest answer is that React's popularity itself is a real, practical advantage — more Stack Overflow answers, more people who already know it.

**Why Vite, not Create React App or Webpack directly:** Vite starts a dev server almost instantly and updates the browser near-instantly on save (via native ES modules during development, instead of bundling the whole app on every change like older tools). Create React App is effectively unmaintained at this point; configuring Webpack by hand is a lot of setup for little benefit on a project this size.

**Why TypeScript, not plain JavaScript:** TypeScript adds static types on top of JavaScript, checked *before* the code ever runs. Concretely in this codebase: [`lib/api.ts`](../frontend-react/src/lib/api.ts) defines exact types for every API response (`Complaint`, `UserProfile`, `WorkerSummary`), so if the backend's response shape and the frontend's assumption about it ever drift apart, that mismatch is far more likely to be caught while writing the code (or at build time) than discovered as a runtime crash a user actually hits. `npm run build` runs `tsc -b` (the TypeScript compiler) before Vite even bundles anything — a type error fails the build outright.

---

## 3. Component structure: pages, components, lib

This is a deliberate three-way split, and being able to explain *why* something lives where matters more than memorizing the file list:

- **`pages/`** — one file per full screen (`CitizenDashboard.tsx`, `WorkerDashboard.tsx`, etc.), each wired to a specific URL in `App.tsx`. A page owns whatever state is specific to that one screen.
- **`components/`** — reusable pieces used *across* more than one page, or complex enough to deserve their own file even if only used once (e.g., `ComplaintTracker.tsx`, the step-tracker widget, or `AddWorkerModal.tsx`, a form used only from `AdminDashboard.tsx` but pulled out for readability).
- **`lib/`** — logic that isn't a visual thing at all: talking to the backend (`api.ts`), remembering who's logged in (`auth.tsx`), which language the UI is in (`uiLang.tsx`), theme (`theme.tsx`), and the one genuinely complex piece of frontend logic in the app, voice recording (`useAudioRecorder.ts` — see [§6](#6-the-most-complex-piece-useaudiorecorderts)).

**The routing table** (`App.tsx`) is intentionally the *only* place that maps a URL to a page and a required role — see [§4](#4-routing-and-route-protection).

---

## 4. Routing, and route protection

`react-router-dom` maps URL paths to components — `/citizen` renders `CitizenDashboard`, `/worker` renders `WorkerDashboard`, etc. (`App.tsx`).

Every dashboard route is wrapped in `<ProtectedRoute allowedRoles={[...]}>`. This is a small but important pattern to understand fully: **this is a UX convenience, not a real security boundary.** It stops a logged-out or wrong-role user from *seeing* a page they shouldn't (redirecting them to `/login` or their own dashboard instead) — but the actual, unavoidable enforcement of who can do what happens on the *backend* (see [`docs/AUTHENTICATION.md`](AUTHENTICATION.md)), because a frontend route guard can always be bypassed by someone editing the JavaScript or calling the API directly. **This distinction — frontend checks are for UX, backend checks are the real security boundary — is one of the single most common things asked about in a full-stack interview**, and this codebase is a clean, concrete example of getting it right: `ProtectedRoute` improves the experience; `require_role(...)` in `deps.py` is what actually prevents anything.

---

## 5. State management: why no Redux (or similar)

A common interview question: "how do you manage state in a React app?" This project's honest answer is deliberately simple, and the simplicity itself is worth explaining, not apologizing for.

Global state that many components need (who's logged in, what language, what theme) uses React's built-in **Context API** — `AuthProvider`, `UiLangProvider`, `ThemeProvider` in `main.tsx`, each wrapping the whole app once. A component anywhere in the tree calls `useAuth()` or `useUiLang()` to read/update that shared state, without it being manually passed down through every intermediate component ("prop drilling").

**Why not Redux (or Zustand, Jotai, etc.)?** Those libraries solve problems that show up in *large, complex* apps: state that needs to be updated from many unrelated places with predictable, debuggable, sometimes time-travel-able history, or state where performance from excessive re-renders becomes a real problem. This app has exactly three pieces of genuinely global state (auth, UI language, theme), each simple and each only changing in a couple of well-understood places. Context is the right-sized tool for that; reaching for Redux here would be solving a problem this app doesn't actually have. **Being able to say "I chose the simpler option because the complexity Redux solves for doesn't apply here" is a stronger interview answer than knowing Redux exists.**

Everything else — a dashboard's list of complaints, a form's current input values — is plain **local component state** (`useState`), because nothing outside that one component needs it.

---

## 6. The most complex piece: `useAudioRecorder.ts`

Worth calling out specifically because it's genuinely the most technically involved file in the frontend, and a good one to be able to walk through in detail if asked "tell me about a hard bug you fixed" or "tell me about the most complex piece of code you wrote."

Browsers record audio via the `MediaRecorder` API. The complication: Sarvam's speech-to-text API hard-rejects any single request over 30 seconds (see [`docs/AI_AGENT.md`](AI_AGENT.md)), but a citizen describing a real problem often talks longer than that. The fix is to stop and immediately restart the recorder every ~28 seconds, producing several independent, valid audio files ("segments") instead of one long one — invisibly, from the citizen's point of view.

**A real bug caught and fixed during development, worth knowing as a concrete story:** the first version of this reused one shared array to collect each segment's audio data, resetting it every time a new segment started. But `MediaRecorder`'s final `ondataavailable`/`onstop` events for the *old* segment fire **asynchronously**, after `.stop()` is called — so resetting the shared array for the *new* segment could race with the *old* segment's still-pending final chunk of data, corrupting both. The fix: give every segment its own array, created fresh and captured by closure inside `startSegmentRecorder()`, so there's no shared mutable state between segments at all — making the race impossible by construction, rather than trying to avoid triggering it. This is a genuinely good, concrete example of the general principle "eliminate shared mutable state instead of carefully sequencing around it."

---

## 7. Talking to the backend: `api.ts`

Every single backend call the frontend makes goes through one file, `lib/api.ts`, rather than being scattered across every component that needs data. Each function has a precise TypeScript return type matching the backend's actual response shape (`Complaint`, `UserProfile`, etc.) — so `api.listComplaints(token, lang)` returning something is a *typed* `Complaint[]`, not an untyped blob a component has to guess the shape of.

`request()`, the one shared function underneath every call, centralizes: attaching the `Authorization: Bearer <token>` header when a token is provided, turning a non-OK HTTP response into a thrown `ApiError` (with the backend's actual error message extracted), and handling a totally-failed network request (server unreachable) with a clear message instead of an unhandled exception. Every page's error handling (`catch (err) { setError(err instanceof ApiError ? err.message : ...) }`) is simple specifically *because* this one shared layer already did the messy part once.

---

## 8. Internationalization (i18n): the UI's own language vs a complaint's language

Two genuinely separate concepts that are easy to conflate, and worth being precise about if asked:

- **UI language** (`lib/i18n.ts`, `lib/uiLang.tsx`) — what language the app's *own* buttons, labels, and messages are shown in. Six languages: English, Hindi, Marathi, Odia, Gujarati, Bengali. `t(lang, "citizen.submit")` looks up the right translated string for the current UI language, from one big dictionary keyed by string ID.
- **Complaint language** — what language a specific complaint's *content* is submitted/displayed in, handled entirely server-side via Sarvam's translation API (see [`docs/AI_AGENT.md`](AI_AGENT.md)) — this has nothing to do with `i18n.ts` at all.

`i18n.ts`'s translations for the 3 newer languages (Odia, Gujarati, Bengali) were generated via Sarvam's own translation API (`scripts/generate_i18n_translations.py`) and hand-reviewed, rather than typed by hand for every string in every language — a practical, honest shortcut for scaling UI translation coverage without a professional translator for languages the original developer doesn't speak.

---

## Likely interview questions about this part of the project

**"Why React over other frameworks?"** — Largest ecosystem and hiring pool; a defensible, if not the only correct, choice for a project this size. See [§2](#2-why-react-vite-and-typescript-specifically).

**"How do you manage state without Redux?"** — Context API for the genuinely global, rarely-changing state (auth, language, theme); local `useState` for everything else. Redux solves problems (complex update patterns, large state trees, time-travel debugging) this app doesn't have. See [§5](#5-state-management-why-no-redux-or-similar).

**"How do you protect routes / handle authorization on the frontend?"** — `ProtectedRoute` redirects based on role, but that's UX only; the backend's `require_role(...)` is the actual security boundary, since any frontend check can be bypassed. See [§4](#4-routing-and-route-protection).

**"Tell me about a tricky bug you fixed."** — The `useAudioRecorder.ts` shared-array race condition: fixed by eliminating shared mutable state between recording segments (closure-local arrays) instead of trying to sequence around the race. See [§6](#6-the-most-complex-piece-useaudiorecorderts).

**"How does your frontend talk to your backend, and how do you handle errors?"** — One central `api.ts` module, typed responses, one shared `ApiError` thrown on any non-OK response, so every page's error handling is uniform and simple. See [§7](#7-talking-to-the-backend-apits).

---

*Related reading: [`docs/BACKEND.md`](BACKEND.md), [`docs/AUTHENTICATION.md`](AUTHENTICATION.md), [`docs/AI_AGENT.md`](AI_AGENT.md), [`docs/PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md).*

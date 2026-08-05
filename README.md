# JanMitra AI

A civic complaint app where a citizen can report a problem (starting with garbage collection) by speaking in their own language. The app transcribes, translates, and routes the complaint to a worker — who sees it in their own language — without the citizen and worker ever needing to share a common language.

**Why it matters:** In India, most civic apps assume citizen and worker share a language. This one doesn't have to.

## Milestone 1 — Working Product

This is the first milestone: a citizen can speak a complaint in Marathi, Hindi, or English; the app transcribes, translates it to English for storage, cleans up obvious spelling mistakes, and generates a short summary; a worker sees the complaint translated into their own chosen language and can mark it resolved; the citizen sees the updated status.

There is no authentication yet — a single hardcoded citizen and a single hardcoded worker are used. See `future_work.md` for what's deliberately out of scope for this milestone.

## Architecture

```
Citizen (Streamlit)                             Worker (Streamlit)
      │                                                │
      │  speak / type + optional photo                 │  view translated complaints
      ▼                                                ▼
                       FastAPI Backend
                             │
      ┌──────────────┬───────┴────────┬────────────────┐
      ▼              ▼                ▼                ▼
  Sarvam STT   Sarvam Chat       Sarvam Translate   Sarvam Chat
 (voice→text,  Completion        (citizen's lang    Completion
  citizen's    (spelling         → English;         (short
  language)    cleanup, in       on-read →           summary)
               citizen's         worker's lang)
               language)
      │
      ▼
  SQLite (complaints table)
```

All AI calls (speech-to-text, spelling cleanup, translation, and summary generation) go through the **Sarvam AI** SDK — one vendor for everything in this milestone. Direct function calls from FastAPI to Sarvam are used; there is no agent framework, queue, or orchestration layer yet.

Spelling cleanup runs on the citizen's original text, in whatever language they used (Marathi, Hindi, or English) — *before* translation to English, not after. A typo in the citizen's own script would otherwise produce a bad English translation that then gets re-mistranslated on every future read into a worker's chosen display language; fixing it at the source, in the original language, avoids that regardless of which of the three languages was used. The citizen's own `original_text` record is never altered — only the working copy fed into translation is normalized.

## Tech Stack

- **Frontend:** Streamlit (separate citizen and worker apps)
- **Backend:** FastAPI
- **Database:** SQLite (via SQLAlchemy)
- **AI:** Sarvam AI — `saaras:v3` for speech-to-text, `sarvam-translate:v1` for translation, `sarvam-105b` for chat-completion-based summaries
- **Storage:** Local filesystem for photos

## Project Structure

```
janmitra-ai/
├── backend/
│   ├── config.py              # All settings, loaded from .env
│   ├── main.py                # FastAPI app entry point
│   ├── models.py               # SQLAlchemy Complaint model
│   ├── database.py             # Engine/session setup
│   ├── routes/complaints.py    # POST/GET/PATCH /complaints
│   └── services/
│       ├── sarvam_client.py         # STT + translation via Sarvam SDK
│       ├── translation_service.py   # Language-code mapping + translate calls
│       ├── normalization_service.py # Spelling cleanup via Sarvam chat completion
│       ├── summary_service.py       # Summary via Sarvam chat completion
│       └── complaint_agent.py       # Orchestrates the full pipeline + storage
├── frontend/
│   ├── citizen_app.py          # Citizen-facing Streamlit app
│   └── worker_app.py           # Worker-facing Streamlit app
├── prompts/                    # Prompt text, never hardcoded in code
├── uploads/                    # Stored complaint photos
├── tests/                      # pytest unit + API tests (mocked AI calls)
├── requirements.txt
├── .env.example
└── future_work.md              # Everything explicitly deferred to later milestones
```

## Setup

1. **Clone and install dependencies**

   ```bash
   git clone https://github.com/sumya24/janmitra-ai
   cd janmitra-ai
   pip install -r requirements.txt
   ```

2. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   | Variable | Description |
   |---|---|
   | `SARVAM_API_KEY` | Your Sarvam AI subscription key (used for STT and translation) |
   | `SARVAM_BASE_URL` | Sarvam API base URL (defaults to `https://api.sarvam.ai`) |
   | `LLM_API_KEY` | Key used for summary generation via Sarvam's chat completion API. Leave blank to reuse `SARVAM_API_KEY`. |
   | `LLM_MODEL` | Chat model used for summaries (defaults to `sarvam-105b`) |
   | `UPLOAD_FOLDER` | Local folder for stored complaint photos (defaults to `uploads`) |
   | `DATABASE_URL` | SQLite connection string |
   | `BACKEND_URL` | URL the Streamlit apps use to reach the FastAPI backend |

   Get a Sarvam AI API key at [sarvam.ai](https://www.sarvam.ai/).

3. **Run the backend**

   ```bash
   uvicorn backend.main:app --reload
   ```

   API docs available at `http://localhost:8000/docs`.

4. **Run the frontends** (in separate terminals)

   ```bash
   streamlit run frontend/citizen_app.py --server.port 8501
   streamlit run frontend/worker_app.py --server.port 8502
   ```

## Demo Workflow

1. Open the citizen app, choose **Marathi**, and either record or type a complaint (e.g. "कचरा उचलला नाही" — "Garbage has not been collected").
2. Optionally attach a photo.
3. Submit — the backend transcribes (if voice), translates to English, and generates a summary.
4. Open the worker app, choose **Hindi**, and see the same complaint translated into Hindi along with its summary.
5. Click **Mark Resolved** on the worker app.
6. Refresh the citizen app — the complaint now shows **Resolved**.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/complaints` | Create a complaint from typed text or a voice recording, with an optional photo |
| `GET` | `/complaints?lang=hi` | List complaints, translating the display text into `lang` on read |
| `PATCH` | `/complaints/{id}` | Update a complaint's status (`open` or `resolved`) |

## Testing

```bash
pytest tests/ -v
```

Tests mock all external AI calls (Sarvam STT, translation, and summary) so they run without any API keys configured.

## Screenshots

_Screenshots will be added here once the app has been run against a live Sarvam AI key._

## Roadmap

See `future_work.md` for the full list. In short:

- **Milestone 2:** real auth, PostgreSQL, photo analysis, category/priority detection, live status updates, maps
- **Milestone 3:** multi-agent orchestration, queues, Docker/AWS deployment, observability tooling

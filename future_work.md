# Future Work

Ideas and requirements that are explicitly out of scope for Milestone 1.
Nothing in this file should be implemented until its milestone arrives.

## Milestone 2 — Intelligent Product

- JWT auth, real user/worker roles (replace hardcoded citizen/worker IDs)
- PostgreSQL (replace SQLite)
- Vision analysis of complaint photos
- Category detection, priority detection, structured JSON output from the LLM
- Retry logic and smarter error recovery for AI calls
- Better UI, live status updates (polling/websockets), maps
- Playwright integration tests
- Accept / reject / reassignment workflow for workers
- Multiple workers, worker areas/zones

## Milestone 3 — Production Product

- LangGraph multi-agent orchestration
- Tool calling, Redis, async queues
- Docker, AWS deployment
- Prometheus, Grafana, OpenTelemetry, Alertmanager
- Centralized logging, CI/CD

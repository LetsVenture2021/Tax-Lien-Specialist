# Tax Lien Strategist – AGI-Enhanced Investment & Reasoning Platform

## Overview

Tax Lien Strategist is a full-stack, agent-assisted investment analysis platform focused on sourcing, evaluating, and managing tax lien assets. The system combines a FastAPI service, a React/Vite front end, orchestration agents, and background workers to deliver an explainable workflow for acquisition through portfolio management.

## Current Highlights

- FastAPI backend wired through an application factory, shared logging, environment-driven settings, and an async SQLAlchemy session helper.
- Celery worker process configured for Redis-backed task execution with an initial health check task.
- React/Vite front end bootstrapped with React Router and React Query; the Reasoning Explorer route is stubbed for future tooling work.
- Docker Compose stack providing backend, worker, frontend, PostgreSQL, and Redis services driven from `.env.example` values.
- Documentation suite centralized under `docs/`, with `docs/implementation_index.md` tracking progress against the specifications.

## Repository Layout

```text
backend/              FastAPI application source and worker entry point
  app/
    api/              API routers and dependencies
    core/             Settings and logging configuration
    db/               Database engine and session helpers
    ai/, jobs/, models/, repositories/, schemas/, services/
frontend/             React application (Vite, TypeScript)
infra/                Infrastructure-as-code placeholders
scripts/              Utility scripts (seeders, automation stubs)
tests/                Backend and frontend tests (planned)
docs/                 Functional, architectural, and implementation specifications
docker-compose.yml    Local development orchestrator
.env.example          Shared environment variable defaults
```

## Backend Service

- Entry point defined in `backend/app/main.py` with CORS support and a `/health` endpoint.
- Global settings supplied via `backend/app/core/config.py` using Pydantic settings tied to `.env` files.
- Structured logging handled by `backend/app/core/logging.py`, integrating Python logging with structlog.
- Async SQLAlchemy session management available through `backend/app/db/session.py` and exposed as a FastAPI dependency in `backend/app/api/deps.py`.
- Celery worker configured in `backend/app/worker.py` with Redis broker/result backend.

The domain routers (`backend/app/api/v1`) and feature packages (`models`, `schemas`, `services`, `jobs`, `ai`) are ready for implementation guided by the specs in `docs/`.

## Frontend Application

- Bootstrapped with Vite, React 18, TypeScript, React Router, and React Query.
- `frontend/src/main.tsx` configures the React Query client and BrowserRouter.
- `frontend/src/App.tsx` defines the initial routing shell and integrates the Reasoning Explorer stub from `frontend/src/features/reasoning-explorer`.
- Tailwind CSS tooling is available via dev dependencies; styling scaffold will follow during feature build-out.

## Documentation Map

- `docs/implementation_index.md` – execution tracker linking requirements to implementation.
- `docs/backend_api_specification.md` – HTTP resource contracts for all planned endpoints.
- `docs/business_rules_and_validation_spec.md` – eligibility, underwriting, and workflow rules.
- `docs/data_model_tax_lien_strategist.md` – relational schema and entity relationships.
- `docs/background_jobs_and_scheduling.md` – schedule outlines for Celery tasks.
- `docs/agent_protocol_and_tools.md` – agent roles, tool interfaces, and prompt conventions.
- Additional design deep dives cover the AGI layer, Reasoning Explorer UI/UX, deployment stacks, and system diagrams.

Refer to `docs/tax_lien_strategist_readme.md` for the original concept brief and `docs/updated_readme.md` for historical context.

## Local Development

1. Copy `.env.example` to `.env` and adjust secrets as needed.
2. Launch the full stack with Docker:

   ```bash
   docker compose up --build
   ```

3. The API is available at `http://localhost:8000`, and the web client runs at `http://localhost:5173`.

Docker now provisions PostgreSQL via the `ankane/pgvector` image so the `vector` extension is available out of the box.

### Running Services Without Docker

Backend (requires Poetry):

```bash
cd backend
poetry install
poetry run uvicorn app.main:create_app --factory --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

### Tests

Automated test scaffolding will live under `tests/`. Pytest and frontend testing tools are already listed in the respective dependency manifests and will be wired in future iterations.

For a quick migration smoke test (ensuring the latest Alembic revision can downgrade and reapply), run:

```bash
DATABASE_URL=postgresql+asyncpg://USER:PASS@HOST:PORT/DB scripts/migration_smoke_test.sh
```

The script expects a running PostgreSQL instance (e.g., the compose pgvector service) and will execute `alembic upgrade head`, `alembic downgrade -1`, and `alembic upgrade head` via Poetry.

## Deployment References

- Azure guidance: `docs/azure_stack_and_deployment_plan_tax_lien_strategist.md`
- GCP guidance: `docs/gcp_stack_and_deployment_plan_tax_lien_strategist.md`
- Infrastructure patterns and final target layout: `docs/final_repo_structure_and_codex_prompt_FULL.md` and `docs/implementation_artifacts_tax_lien_strategist.md`

## Contact

Pryceless Ventures LLC

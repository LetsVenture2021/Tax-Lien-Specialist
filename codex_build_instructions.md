# Codex Build Instructions – Tax Lien Strategist + AGI / Reasoning Explorer

Version: v1  
Audience: GPT‑5.1 Codex Agent (and human devs supervising it)

This document provides a **step-by-step plan** for the GPT‑5.1 Codex Agent to convert the existing markdown specifications into a fully working application.

All instructions assume the repo contains the `.md` files listed in `/docs` and that the target stack is:
- Backend: **FastAPI + PostgreSQL + Redis + Celery (or equivalent)**
- Frontend: **React + TypeScript + Vite**
- AI Layer: OpenAI GPT‑5.1 + HuggingFace

Codex should follow these steps in order, minimizing guesswork and adhering strictly to the specifications already provided.

---
## 0. Pre-Flight: Ingest Specifications

1. **Parse the `/docs` directory** and locate at least the following files:
   - `tax_lien_strategist_readme.md` / `UPDATED_README.md`
   - `system_architecture_diagram.md`
   - `formal_dfd_spec.md`
   - `level_3_deep_dive_deal_engine.md`
   - `diagram_suite_agi_agentic_system.md`
   - `data_model_tax_lien_strategist.md`
   - `analytical_extensions_tax_lien_strategist.md`
   - `agi_agentic_system_whitepaper.md`
   - `agi_layer_extensions_tax_lien_strategist.md`
   - `implementation_artifacts_tax_lien_strategist.md`
   - `reasoning_explorer_technical_implementation_plan.md`
   - `reasoning_explorer_ui_design.md`
   - `reasoning_explorer_user_stories.md`
   - `backend_api_specification.md`
   - `business_rules_and_validation_spec.md`
   - `background_jobs_and_scheduling.md`
   - `agent_protocol_and_tools.md`
   - `environment_variables_and_config_reference.md`
   - `ci_cd_pipeline_specification.md`
   - `local_development_guide.md`
   - `database_schema_ddl.md`
   - `seed_data_and_test_fixtures.md`
   - `logging_monitoring_and_slos.md`
   - `incident_response_runbooks.md`
   - Cloud-specific stack docs (Azure and/or GCP)

2. **Build an internal knowledge map**:
   - Map each domain (investors, properties, liens, analysis, portfolios) to:
     - Data model
     - API endpoints
     - Business rules
     - Background jobs
     - Agent interactions

3. **Do not invent behavior** that contradicts the specifications. If something is ambiguous:
   - Prefer the more conservative/security-aware interpretation.
   - Leave `TODO` comments where a business decision is required.

---
## 1. Repository Bootstrap

Create the base repo structure as described in the folder architecture docs and README.

### 1.1 Root Files
- `README.md` – use the updated README content.
- `.gitignore` – Python, Node, IDE, OS-specific ignores.
- `docker-compose.yml` – orchestrate:
  - `backend`
  - `worker`
  - `frontend`
  - `postgres`
  - `redis`

### 1.2 Backend Project Setup
- Create `backend/` directory.
- Add Python project files:
  - `pyproject.toml` **or** `requirements.txt` with dependencies:
    - `fastapi`, `uvicorn[standard]`
    - `sqlalchemy`, `alembic`
    - `psycopg` / `asyncpg`
    - `redis`, `celery` (or chosen job framework)
    - `pydantic`
    - `httpx` or `requests`
    - `python-jose`, `passlib`
    - `structlog` or logging extras
    - OpenAI + HF clients
  - `backend/Dockerfile` per deployment docs.

### 1.3 Frontend Project Setup
- Create `frontend/` directory.
- Initialize Vite React + TypeScript project.
- Install dependencies:
  - `react`, `react-dom`, `react-router-dom`
  - `@tanstack/react-query`
  - `axios` or `fetch` wrapper
  - `tailwindcss` + `postcss` + `autoprefixer`
  - Optional UI libs (e.g., shadcn/ui, radix)

---
## 2. Backend Implementation Plan

### 2.1 Core FastAPI Structure

Create under `backend/app/`:
- `main.py` – app factory, router mounting, CORS, middleware.
- `core/` – config, logging, security.
- `db/` – session, engine, base.
- `models/` – SQLAlchemy models mapping to `database_schema_ddl.md` and `data_model_tax_lien_strategist.md`.
- `schemas/` – Pydantic models for API I/O aligned with `backend_api_specification.md`.
- `services/` – business logic matching `business_rules_and_validation_spec.md`.
- `api/v1/` – route modules per domain.
- `ai/` – LLM client, memory, reasoning logger, agent orchestration.
- `jobs/` – background tasks per `background_jobs_and_scheduling.md`.

### 2.2 Implement Models
Using `database_schema_ddl.md` and `data_model_tax_lien_strategist.md`:
- Implement SQLAlchemy models for:
  - `investors`
  - `properties`
  - `liens`
  - `counties`
  - `analysis_runs`
  - `deals` / candidate deals (if modeled)
  - `portfolios`, `portfolio_holdings`
  - `documents`, `notifications`
  - AI tables:`ai_agent_episodes`, `ai_agent_memories`, `ai_llm_calls`, `ai_llm_tool_events`, `ai_llm_decision_events`, `ai_embeddings`
- Ensure foreign keys and indexes match the DDL.

### 2.3 Implement Schemas (Pydantic)
For each endpoint defined in `backend_api_specification.md`:
- Create request/response schemas.
- Enforce data shapes and constraints as described.

### 2.4 Services & Business Rules
Implement service modules that:
- Enforce all rules in `business_rules_and_validation_spec.md`.
- Provide functions like:
  - `create_investor`, `update_investor`, `archive_investor`
  - `list_liens`, `get_lien`, `transition_lien_status`
  - `start_analysis_run`, `compute_candidate_deals`
  - `calculate_deal_metrics`
  - `recalculate_portfolio_nav`
- Fail fast with well-defined error codes (`INVALID_STATUS_TRANSITION`, `BUDGET_EXCEEDED`, etc.).

### 2.5 Routes
Map services to routes as defined in `backend_api_specification.md`:
- `auth_routes.py`
- `investor_routes.py`
- `property_routes.py`
- `lien_routes.py`
- `analysis_routes.py`
- `portfolio_routes.py`
- `documents_routes.py`
- `notifications_routes.py`
- `agents_routes.py`
- `reasoning_explorer_routes.py`

Ensure:
- Role-based access enforced via dependencies.
- Pagination and error formats follow spec.

### 2.6 AI / Agent Layer
Under `backend/app/ai/`:
- `llm_client.py` – unified interface for GPT‑5.1 + HF.
- `embedding_client.py` – embeddings via OpenAI or HF.
- `memory/` – episodic and semantic memory abstractions.
- `reasoning_logger.py` – writes to all AI tables.
- `orchestrator_service.py`, `research_agent_service.py`, `underwriting_agent_service.py`, `document_agent_service.py` implementing `agent_protocol_and_tools.md`.

Agent behavior must:
- Log every LLM call.
- Use tools with JSON I/O schemas from `agent_protocol_and_tools.md`.
- Be stateless across invocations except via DB state and memory tables.

### 2.7 Background Jobs
Implement Celery (or equivalent) tasks corresponding to `background_jobs_and_scheduling.md`:
- County ingestion
- Valuation refresh
- NAV recalculation
- Reasoning log cleanup
- Document generation
- Notification sending

Use `environment_variables_and_config_reference.md` for schedule and retry parameters.

---
## 3. Frontend Implementation Plan

### 3.1 Base Setup

In `frontend/`:
- Configure Vite + React Router + React Query.
- Set API base URL from `VITE_API_URL`.

### 3.2 Features

Implement feature folders aligned with API spec and UI docs:
- `/features/auth`
- `/features/investors`
- `/features/properties`
- `/features/liens`
- `/features/analysis`
- `/features/portfolios`
- `/features/documents`
- `/features/notifications`
- `/features/reasoning-explorer`

Use `reasoning_explorer_ui_design.md` + `reasoning_explorer_user_stories.md` + `reasoning_explorer_technical_implementation_plan.md` to implement:
- Episodes list & detail pages
- Timeline view
- Task tree
- LLM call & decision detail drawers
- Settings panels

Respect redaction behavior described in AI docs:
- Do not render full prompts if settings disallow it.

### 3.3 Shared Components
Create reusable components as per architecture docs:
- Tables, modals, forms, filters
- Layout (sidebar, header, content)
- Loading and error states

---
## 4. Data & Seed Scripts

### 4.1 Migrations
- Initialize Alembic.
- Create migration for initial schema based on `database_schema_ddl.md`.

### 4.2 Seed Data
- Implement `scripts/seed_dev_data.py`:
  - Read JSON from `seed_data_and_test_fixtures.md` (converted to concrete `.json` files or inline definitions).
  - Insert baseline investors, counties, properties, liens.

---
## 5. Observability & Logging

Follow `logging_monitoring_and_slos.md`:
- Implement structured logging using JSON.
- Include required log fields.
- Add basic metrics endpoints or middleware if appropriate.

For Reasoning Explorer:
- Ensure AI tables are populated during agent activity.
- Provide enough fields for the frontend to render a coherent timeline.

---
## 6. CI/CD & Dev Experience

Using `ci_cd_pipeline_specification.md`:
- Create `.github/workflows/ci.yml`:
  - Backend tests, lint
  - Frontend tests, lint
- Create `.github/workflows/deploy.yml` skeleton:
  - Build & push Docker images
  - Deploy to selected cloud (Azure or GCP stack docs)

Use `local_development_guide.md` to ensure:
- `docker-compose` works end-to-end
- Developers can run backend & frontend locally with seeded data

---
## 7. Validation & Testing

### 7.1 Unit Tests
- Implement backend unit tests for:
  - Business rules (yield, LTV, status transitions)
  - Agents’ tool-calling behavior (mock LLM)

### 7.2 Integration Tests
- API tests for main endpoints.
- AGI/Reasoning flows:
  - Trigger analysis run
  - Ensure episodes + LLM calls + decisions are logged

### 7.3 Frontend Tests
- Component tests for Reasoning Explorer views.
- End-to-end tests for a core user journey: run analysis → view reasoning → view portfolio.

---
## 8. Ambiguity & TODO Handling

If the specification is **silent or ambiguous** about a detail:
- **Do not invent business rules.**
- Choose defaults that are safe, minimal, and easy to change.
- Leave `// TODO:` or `# TODO:` comments clearly explaining:
  - What is missing
  - What assumption was temporarily made

Example:
```python
# TODO: Confirm whether we must block analysis runs when investor is inactive.
```

---
## 9. Completion Criteria

Codex should consider the implementation complete when:

1. All endpoints in `backend_api_specification.md` compile and pass basic tests.
2. All core business rules from `business_rules_and_validation_spec.md` are enforced.
3. Reasoning Explorer can:
   - List episodes
   - View episode details
   - Inspect LLM calls and decisions
4. Background jobs from `background_jobs_and_scheduling.md` exist as Celery tasks (or equivalent) and can be scheduled.
5. Local environment can be started with `docker compose up` and accessed via browser.
6. At least one example analysis run, with a corresponding reasoning episode, can be executed end-to-end in dev.

At that point, the system is a coherent, runnable implementation aligned with the provided specifications and ready for further refinement and production hardening.


# Reasoning Explorer – Technical Implementation Plan

Scope: Implement the **Reasoning Explorer UI** and supporting backend for inspecting AGI/LLM episodes, calls, decisions, and memories in the Tax Lien Strategist App.

Audience: Tech lead, backend engineers, frontend engineers, DevOps, data/ML engineers.

---
## 1. Overall Architecture

### 1.1 High-Level Components

- **Frontend (Admin/Dev UI)**
  - React + TypeScript + TailwindCSS
  - Route namespace: `/admin/reasoning-explorer/*`
  - Uses existing auth/session from main app

- **Backend (API Services)**
  - Python (FastAPI) or Node (NestJS/Express) – assume FastAPI for concreteness
  - New module/namespace: `reasoning_explorer`
  - REST/JSON API endpoints for:
    - Episodes
    - LLM calls
    - Decisions
    - Entities → linked episodes/decisions
    - Settings (redaction/retention) – admin only

- **Data Layer**
  - Reuse existing tables:
    - `agent_tasks`, `ai_agent_episodes`, `ai_llm_calls`, `ai_llm_tool_events`, `ai_llm_decision_events`, `ai_agent_memories`, `ai_agent_working_sets`
  - Read-only for most endpoints (settings endpoints write to config table or config store)

- **Auth & RBAC**
  - Use existing user roles (`dev`, `compliance`, `analyst`)
  - Enforce role checks at backend endpoint level + feature gating in frontend

---
## 2. Backend Design (FastAPI)

### 2.1 API Namespace & Versioning

Base path: `/api/admin/reasoning/v1`

Planned route groups:
- `/episodes`
- `/llm-calls`
- `/decisions`
- `/entities`
- `/settings`

### 2.2 Data Access Layer

Create a dedicated module `reasoning_explorer/repository.py` with:

- `list_episodes(filters, pagination)`
- `get_episode_detail(episode_id)`
- `list_episode_events(episode_id, filters)`
- `list_llm_calls(filters, pagination)`
- `get_llm_call(call_id)`
- `list_decisions(filters, pagination)`
- `get_decision(decision_id)`
- `search_entities(query)`
- `get_entity_context(entity_type, entity_id)`
- `get_settings()`
- `update_settings(payload)`

Use SQLAlchemy for querying; leverage indices:
- `ai_agent_episodes_agent_type_idx`
- `ai_llm_calls_task_idx`, `ai_llm_calls_episode_idx`
- `ai_llm_decision_events_episode_idx`
- `ai_agent_memories_episode_idx`

### 2.3 Example Endpoint Specs

#### 2.3.1 List Episodes

**GET** `/episodes`

**Query params:**
- `page: int = 1`
- `page_size: int = 50`
- `agent_type: str | None`
- `status: str | None`
- `date_from: datetime | None`
- `date_to: datetime | None`
- `search: str | None` (episode_id, root_task_name, county_name)

**Response:**
```json
{
  "items": [
    {
      "id": 123,
      "episode_uuid": "...",
      "agent_type": "orchestrator",
      "status": "completed",
      "root_task_id": 456,
      "root_task_name": "Analyze County X",
      "analysis_run_id": 789,
      "started_at": "2025-11-20T10:00:00Z",
      "completed_at": "2025-11-20T10:05:30Z",
      "duration_ms": 330000,
      "llm_call_count": 42,
      "decision_count": 15
    }
  ],
  "page": 1,
  "page_size": 50,
  "total": 1023
}
```

#### 2.3.2 Get Episode Detail

**GET** `/episodes/{episode_id}`

Returns:
- Episode metadata
- Root task summary
- Aggregate counts

**GET** `/episodes/{episode_id}/tasks`

Returns tree of tasks: `{ id, parent_task_id, agent_type, status, task_name }`.

**GET** `/episodes/{episode_id}/events`

Query params:
- `event_types: list[str]` (subset of `llm_call`, `tool_event`, `decision`, `memory`)
- `task_id: int | None`

Response:
```json
{
  "items": [
    {
      "event_id": 1,
      "event_type": "llm_call",
      "created_at": "...",
      "agent_task_id": 456,
      "summary": "UnderwritingAgent: compute scenarios for lien 123",
      "llm_call_id": 111
    },
    {
      "event_id": 2,
      "event_type": "decision",
      "decision_id": 222,
      "summary": "select_top_deals: 5 candidates selected"
    }
  ]
}
```

#### 2.3.3 LLM Calls

**GET** `/llm-calls`

Filters for model, date range, agent_type, latency, token counts.

**GET** `/llm-calls/{id}`

Payload includes:
- Possibly redacted `prompt` / `response`
- `tool_calls` JSON
- Model parameters & stats

Redaction logic enforced based on settings + user role.

#### 2.3.4 Decisions

**GET** `/decisions` and `/decisions/{id}` similar to LLM calls; `decision_payload` JSON and links to related entities.

#### 2.3.5 Entities

**GET** `/entities/search`

Query params: `q`

Returns union of:
- Matching liens (`id`, certificate number, property address, county)
- Properties (`id`, address, APN, county)
- Investors (`investor_profile_id`, display_name)
- Analysis runs (`id`, type, county, created_at)

**GET** `/entities/{entity_type}/{entity_id}`

Returns:
- Entity summary
- Related episodes
- Related decisions
- Related documents

#### 2.3.6 Settings

**GET** `/settings`

**PATCH** `/settings`

Body example:
```json
{
  "store_full_prompts": false,
  "store_redacted_prompts": true,
  "store_full_responses": false,
  "store_embeddings_only": true,
  "log_retention_days": 90
}
```

Backend persists to a config table, e.g., `ai_reasoning_settings` with a single-row pattern or per-environment key.

---
## 3. Frontend Design (React/TypeScript)

### 3.1 Route Structure

Base: `/admin/reasoning-explorer`

Routes:
- `/episodes`
- `/episodes/:episodeId`
- `/llm-calls`
- `/decisions`
- `/entities`
- `/settings`

Use React Router (or Next.js routing if integrated into Next).

### 3.2 State Management

Use **React Query (TanStack Query)** for data fetching + caching:

- Query keys:
  - `['episodes', filters]`
  - `['episode', episodeId]`
  - `['episode-events', { episodeId, filters }]`
  - `['llm-calls', filters]`
  - `['llm-call', id]`
  - `['decisions', filters]`
  - `['decision', id]`
  - `['entities-search', q]`
  - `['entity-detail', entityType, entityId]`
  - `['reasoning-settings']`

### 3.3 Component Tree (Key Components)

- `ReasoningExplorerLayout`
  - Left nav (Episodes, LLM Calls, Decisions, Entities, Settings)
  - Main content outlet

- `EpisodesListPage`
  - `EpisodesFilterBar`
  - `EpisodesTable`

- `EpisodeDetailPage`
  - `EpisodeHeaderCard`
  - `TaskTreePanel`
  - `TimelinePanel`
  - `ContextPanel`

- `TimelinePanel`
  - `TimelineFilters` (toggles for event types, task filter indicator)
  - `TimelineEventList` (virtualized list)
  - `TimelineEventItem`

- `LLMCallDetailDrawer`
- `ToolEventDetailDrawer`
- `DecisionDetailDrawer`

- `LLMCallsPage`
  - `LLMCallsFilterBar`
  - `LLMCallsTable`

- `DecisionsPage`
  - `DecisionsFilterBar`
  - `DecisionsTable`

- `EntitiesPage`
  - `EntitySearchBar`
  - `EntitySearchResults`
  - `EntityDetailTabs`

- `SettingsPage`
  - `RedactionSettingsForm`
  - `RetentionSettingsForm`

### 3.4 UI/UX Details

- Use Tailwind CSS for layout and styling; maintain consistency with existing admin UI.
- Timeline uses virtualization (e.g., react-window or react-virtualized) for performance.
- JSON payloads (tool_input, tool_output, decision_payload) rendered using a collapsible JSON viewer component.
- Long text (prompts/responses) truncated by default with "Show more" toggles.

---
## 4. Security & RBAC

### 4.1 Backend Enforcement

- Decorator or dependency
  - `require_role(['dev', 'compliance', 'analyst'])` for read endpoints
  - `require_role(['compliance', 'admin'])` for `/settings` write

- Role resolution from existing auth token/session (e.g., JWT claims or DB lookup).

### 4.2 Frontend Gating

- Use a `useCurrentUser()` hook to get role.
- Hide Settings route link for non-compliance/admin users.
- Conditionally hide/show full prompts/responses based on role + settings payload from backend.

---
## 5. Redaction Implementation

### 5.1 Strategy

- Store **full content** in lower environments (dev/staging) by default.
- In production, respect settings:
  - If `store_full_prompts = false`, drop or hash `prompt` on write.
  - If `store_redacted_prompts = true`, store a cleaned version (strip names, addresses via regex/LLM redaction pipeline).

### 5.2 Write-Path Hooks

Wherever `ai_llm_calls` rows are created:
- Apply redaction function based on current settings.
- Redaction function can:
  - Remove obvious PII (emails, phone numbers, SSNs, addresses)
  - Optionally mask property addresses (keep county, city but strip street number).

Implement as a shared library function `redact_prompt_response(prompt, response, settings)` used by the AGI orchestration service.

---
## 6. Performance Considerations

- **Pagination** everywhere (episodes, calls, decisions) – default 50 rows, max 200.
- **Indices**:
  - Already defined on episode_id, agent_task_id, etc.
  - Additional indices on `ai_llm_calls (created_at, model_name)` and `ai_llm_decision_events (created_at, decision_type)` if needed.
- **Timeline virtualization** to handle episodes with 1,000+ events.
- Use `SELECT ... LIMIT/OFFSET` with careful ordering; consider keyset pagination for very large datasets.

---
## 7. Logging & Monitoring

- Add structured logs for all `/reasoning/v1` API calls:
  - `user_id`, `role`, endpoint, response_time, status_code
- Metrics to track:
  - Requests per endpoint
  - Error rates
  - P95 latency
- Optional: feature flag around Reasoning Explorer to control rollout.

---
## 8. Implementation Phases & Milestones

### Phase 1 – Foundations (1–2 sprints)
- [ ] Create DB tables (if not already existing) for episodes, LLM calls, decisions, memories.
- [ ] Implement minimal backend endpoints for `/episodes` list + `/episodes/{id}` detail.
- [ ] Create frontend layout + Episodes list and detail pages (no timeline yet).

### Phase 2 – Timeline & LLM Drilldown (1–2 sprints)
- [ ] Implement `/episodes/{id}/events` backend endpoint.
- [ ] Implement frontend timeline with event type filters.
- [ ] Implement LLM Call detail drawer.

### Phase 3 – LLM Calls & Decisions Catalog (1 sprint)
- [ ] Implement `/llm-calls` and `/llm-calls/{id}` endpoints.
- [ ] Implement `/decisions` and `/decisions/{id}` endpoints.
- [ ] Build catalog pages with filtering and drilldown.

### Phase 4 – Entity-Centric View (1 sprint)
- [ ] Implement `/entities/search` and `/entities/{entity_type}/{entity_id}` endpoints.
- [ ] Build Entities search and detail UI with tabs.

### Phase 5 – Settings & Compliance (1 sprint)
- [ ] Implement `/settings` read/write with role protection.
- [ ] Integrate settings into AGI write-path (redaction pipeline).
- [ ] Build Settings page UI.

### Phase 6 – Hardening (ongoing)
- [ ] Add tests (unit + integration) for key endpoints.
- [ ] Performance tuning with realistic data volumes.
- [ ] UX polish, error handling, and empty state improvements.

---
## 9. Testing Strategy

- **Unit tests** for repository functions (filters, pagination logic).
- **Integration tests** for API endpoints (auth, RBAC, redaction behavior).
- **Frontend tests**:
  - Component tests (e.g., EpisodeDetail, TimelinePanel) with mocked API responses.
  - E2E flows (Cypress/Playwright) for: list episodes → open detail → open LLM call.

- **Load test** selected endpoints with synthetic data:
  - 10k episodes, 100k LLM calls, 50k decisions.

---
## 10. Dependencies & Integration Points

- **Existing auth** system for user roles.
- **AGI orchestration** service to ensure it writes into `ai_llm_calls`, `ai_agent_episodes`, etc.
- **Main Deal Console** for deep links back to business entities (lien/property/analysis run pages).

---
**End of Technical Implementation Plan – Reasoning Explorer**


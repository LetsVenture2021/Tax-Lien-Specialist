# Backend API Specification – Tax Lien Strategist + AGI / Reasoning Explorer

Version: v1  
Audience: GPT‑5.1 Codex Agent, backend engineers, QA

This document defines the **HTTP API contract** for the Tax Lien Strategist application, including the **Reasoning Explorer** and AGI/Agent endpoints.

All endpoints are assumed to be under:

```text
Base URL: /api/v1
Admin / Reasoning Explorer: /api/admin/reasoning/v1
```

---
## 0. Conventions

### 0.1 Common
- All requests and responses use **JSON**.
- Timestamps are ISO 8601 in UTC, e.g. `"2025-11-21T06:00:00Z"`.
- IDs are integers unless otherwise specified.
- Pagination:
  - Query params: `page` (1-based), `page_size`.
  - Response wrapper:
    ```json
    {
      "items": [ ... ],
      "page": 1,
      "page_size": 20,
      "total": 123
    }
    ```

### 0.2 Authentication & Roles
- Authentication: **JWT** bearer token in `Authorization` header.
- Standard roles:
  - `investor`
  - `manager` (fund manager / admin)
  - `dev` (internal developer)
  - `compliance`
  - `analyst`

- Some endpoints require elevated roles (e.g., `dev` or `compliance` for Reasoning Explorer).

Standard error payload:
```json
{
  "detail": "Human-readable error message",
  "code": "ERROR_CODE",
  "meta": { "optional": "context" }
}
```

HTTP status codes:
- 200 / 201 / 204 for success
- 400 for validation errors
- 401 for unauthenticated
- 403 for forbidden
- 404 for not found
- 409 for conflicts
- 500 for unexpected errors

---
## 1. Auth & User Management

### 1.1 Login
**POST** `/auth/login`

Authenticate a user and return a JWT.

**Request body**
```json
{
  "email": "user@example.com",
  "password": "Secret123!"
}
```

**Response 200**
```json
{
  "access_token": "jwt.token.here",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Jane Doe",
    "roles": ["manager", "analyst"]
  }
}
```

### 1.2 Refresh Token (optional if implemented)
**POST** `/auth/refresh`

**Request body**
```json
{
  "refresh_token": "..."
}
```

**Response 200** – same shape as login.

### 1.3 Get Current User
**GET** `/auth/me`

**Auth:** any authenticated user.

**Response 200**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "Jane Doe",
  "roles": ["manager"],
  "created_at": "2025-11-01T10:00:00Z"
}
```

---
## 2. Investors

### 2.1 List Investors
**GET** `/investors`

**Roles:** `manager`, `dev`, `analyst`

**Query params**
- `page`, `page_size`
- `search` (matches name/email)

**Response 200**
```json
{
  "items": [
    {
      "id": 1,
      "display_name": "Alpha Capital LLC",
      "email": "alpha@example.com",
      "phone": "+1-555-123-4567",
      "status": "active"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
}
```

### 2.2 Create Investor
**POST** `/investors`

**Roles:** `manager`

**Request body**
```json
{
  "display_name": "Alpha Capital LLC",
  "email": "alpha@example.com",
  "phone": "+1-555-123-4567",
  "notes": "Primary fund partner"
}
```

**Response 201** – investor object with `id`, timestamps.

### 2.3 Get Investor
**GET** `/investors/{id}`

**Roles:** `manager`, `dev`, `analyst`

**Response 200**
```json
{
  "id": 1,
  "display_name": "Alpha Capital LLC",
  "email": "alpha@example.com",
  "phone": "+1-555-123-4567",
  "notes": "Primary fund partner",
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-11-02T12:00:00Z"
}
```

### 2.4 Update Investor
**PUT** `/investors/{id}`

**Roles:** `manager`

**Request body** – same as create, all fields optional for partial update if using PATCH semantics.

### 2.5 Archive / Delete Investor
**DELETE** `/investors/{id}`

**Roles:** `manager`

Soft-delete recommended: mark `status = archived`.

---
## 3. Properties

### 3.1 List Properties
**GET** `/properties`

**Roles:** `manager`, `analyst`, `dev`

**Query params**
- `page`, `page_size`
- `county_id`
- `state`
- `search` (address, APN)

**Response 200 (items truncated)**
```json
{
  "items": [
    {
      "id": 101,
      "address": "123 Main St",
      "city": "Somewhere",
      "state": "TX",
      "zip": "77777",
      "county_id": 5,
      "apn": "123-456-7890",
      "property_type": "SFR"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 50
}
```

### 3.2 Get Property
**GET** `/properties/{id}`

Returns full property details, including latest valuation (if present).

### 3.3 Create / Update Property
Generally properties come from ingestion & county data. If manual creation is required:

**POST** `/properties`

**PUT** `/properties/{id}`

Simplified body:
```json
{
  "address": "123 Main St",
  "city": "Somewhere",
  "state": "TX",
  "zip": "77777",
  "county_id": 5,
  "apn": "123-456-7890",
  "property_type": "SFR"
}
```

### 3.4 Property Valuations
**GET** `/properties/{id}/valuations`

List historical valuations for a property.

**POST** `/properties/{id}/valuations`

Create a new valuation (usually by an agent/tool):
```json
{
  "as_of": "2025-11-20T00:00:00Z",
  "value": 325000,
  "method": "AVM",
  "source": "Zillow"
}
```

---
## 4. Counties & Liens

### 4.1 List Counties
**GET** `/counties`

List supported counties.

### 4.2 Get County
**GET** `/counties/{id}`

County metadata (name, state, auction types, redemption rules).

### 4.3 List Liens
**GET** `/liens`

**Query params**
- `page`, `page_size`
- `county_id`
- `status` (e.g., `available`, `acquired`, `redeemed`, `defaulted`)
- `investor_id`
- `min_face`, `max_face`
- `min_yield`, `max_yield`

**Response 200 (items truncated)**
```json
{
  "items": [
    {
      "id": 1001,
      "certificate_number": "C-2025-0001",
      "county_id": 5,
      "property_id": 101,
      "face_value": 15000,
      "interest_rate": 0.18,
      "status": "available",
      "auction_date": "2025-01-15T00:00:00Z"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 200
}
```

### 4.4 Get Lien
**GET** `/liens/{id}`

Returns:
- Lien details
- Linked property summary
- Key computed metrics (current yield, estimated redemption timeline if calculated).

### 4.5 Create / Update Lien (Ingestion/Internal)
**POST** `/liens`
**PUT** `/liens/{id}`

Not typically used by front-end; primarily ingestion / admin.

### 4.6 Lien Status Transitions
**POST** `/liens/{id}/status`

**Request body**
```json
{
  "status": "acquired",
  "investor_id": 1,
  "acquired_date": "2025-01-20T00:00:00Z"
}
```

Valid transitions and business rules are defined in the **Business Rules & Validation Spec**.

---
## 5. Analysis Runs & Deal Engine

### 5.1 Create Analysis Run
**POST** `/analysis/runs`

Start a new analysis job for a county or subset of liens.

**Roles:** `manager`, `analyst`

**Request body**
```json
{
  "name": "TX Harris County Jan 2025 Auction",
  "county_id": 5,
  "investor_profile_id": 1,
  "target_yield_min": 0.12,
  "max_budget": 500000,
  "constraints": {
    "max_ltv": 0.7,
    "max_liens_per_property": 1
  }
}
```

**Response 202**
```json
{
  "id": 501,
  "status": "pending",
  "created_at": "2025-11-21T06:05:00Z"
}
```

### 5.2 List Analysis Runs
**GET** `/analysis/runs`

**Query params**
- `page`, `page_size`
- `investor_profile_id`
- `status` (pending / running / completed / failed)

### 5.3 Get Analysis Run Detail
**GET** `/analysis/runs/{id}`

Returns:
- Run metadata
- Status
- Summary metrics (e.g., number of candidate liens, number of deals, total capital required).

### 5.4 List Candidate Deals for a Run
**GET** `/analysis/runs/{id}/deals`

**Response 200 (items truncated)**
```json
{
  "items": [
    {
      "deal_id": 9001,
      "lien_id": 1001,
      "property_id": 101,
      "score": 0.92,
      "expected_yield": 0.16,
      "risk_score": 0.2,
      "investment_amount": 15000
    }
  ],
  "page": 1,
  "page_size": 50,
  "total": 80
}
```

### 5.5 Mark Deal as Selected / Rejected
**POST** `/analysis/runs/{id}/deals/{deal_id}/decision`

**Request body**
```json
{
  "decision": "selected",   
  "reason": "Fits investor yield and risk profile"
}
```

This can optionally trigger agent logging and a decision event.

---
## 6. Portfolios & Holdings

### 6.1 List Portfolios
**GET** `/portfolios`

### 6.2 Create Portfolio
**POST** `/portfolios`

**Request body**
```json
{
  "name": "Alpha Tax Lien Fund I",
  "investor_id": 1,
  "base_currency": "USD"
}
```

### 6.3 Get Portfolio
**GET** `/portfolios/{id}`

Returns:
- Core portfolio data
- Current NAV (if computed)
- Aggregate metrics

### 6.4 List Portfolio Holdings
**GET** `/portfolios/{id}/holdings`

**Response 200 (items truncated)**
```json
{
  "items": [
    {
      "holding_id": 3001,
      "lien_id": 1001,
      "investment_amount": 15000,
      "acquired_date": "2025-01-20T00:00:00Z",
      "status": "active"
    }
  ],
  "page": 1,
  "page_size": 50,
  "total": 10
}
```

### 6.5 Add/Update/Remove Holdings
**POST** `/portfolios/{id}/holdings`
**PUT** `/portfolios/{id}/holdings/{holding_id}`
**DELETE** `/portfolios/{id}/holdings/{holding_id}`

---
## 7. Documents & Notifications

### 7.1 List Documents
**GET** `/documents`

Query by:
- `entity_type` (`lien`, `property`, `portfolio`, `analysis_run`)
- `entity_id`

### 7.2 Get Document Metadata
**GET** `/documents/{id}`

Returns metadata and a signed URL (or path) for download.

### 7.3 Generate Document
**POST** `/documents/generate`

Triggers document agent / template engine.

**Request body**
```json
{
  "template_key": "investment_summary",
  "context": {
    "investor_id": 1,
    "portfolio_id": 10,
    "analysis_run_id": 501
  }
}
```

**Response 202** – returns a job ID or document ID that will be populated when ready.

### 7.4 Notifications

**GET** `/notifications`
- List notifications for current user.

**POST** `/notifications/test`
- Admin-only endpoint to send a test notification.

---
## 8. AGI / Agent Orchestration API

These endpoints expose **high-level orchestration** actions. Internal agent logic remains in services; these APIs are for the app and admin tools.

### 8.1 Trigger Orchestrated Analysis
**POST** `/agents/orchestrator/analysis`

High-level wrapper to start an analysis run that uses agents heavily.

**Request body**
```json
{
  "county_id": 5,
  "investor_profile_id": 1,
  "max_budget": 500000,
  "target_yield_min": 0.12,
  "notes": "Run pre-auction screening"
}
```

**Response 202**
```json
{
  "analysis_run_id": 501,
  "episode_id": 10001,
  "status": "pending"
}
```

### 8.2 Agent Health / Status
**GET** `/agents/status`

Shows latest status of orchestrator, research, underwriting, document agents.

---
## 9. Admin – Reasoning Explorer API

These endpoints are under a separate base path and require dev/compliance roles.

Base: `/api/admin/reasoning/v1`

### 9.1 List Episodes
**GET** `/episodes`

**Roles:** `dev`, `compliance`, `analyst`

**Query params**
- `page`, `page_size`
- `agent_type` (orchestrator, research, underwriting, document)
- `status` (running, completed, failed)
- `date_from`, `date_to`
- `search` (episode UUID, root task name, county name)

**Response 200**
```json
{
  "items": [
    {
      "id": 10001,
      "episode_uuid": "b8b4f8d2-...",
      "agent_type": "orchestrator",
      "status": "completed",
      "root_task_id": 4001,
      "root_task_name": "Analyze Harris County Jan 2025",
      "analysis_run_id": 501,
      "started_at": "2025-11-21T06:00:00Z",
      "completed_at": "2025-11-21T06:05:00Z",
      "duration_ms": 300000,
      "llm_call_count": 42,
      "decision_count": 15
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 10
}
```

### 9.2 Get Episode Detail
**GET** `/episodes/{episode_id}`

Returns:
```json
{
  "id": 10001,
  "episode_uuid": "b8b4f8d2-...",
  "agent_type": "orchestrator",
  "status": "completed",
  "started_at": "2025-11-21T06:00:00Z",
  "completed_at": "2025-11-21T06:05:00Z",
  "duration_ms": 300000,
  "analysis_run_id": 501,
  "root_task_id": 4001,
  "root_task_name": "Analyze Harris County Jan 2025"
}
```

### 9.3 Get Episode Task Tree
**GET** `/episodes/{episode_id}/tasks`

**Response 200**
```json
[
  {
    "id": 4001,
    "parent_task_id": null,
    "agent_type": "orchestrator",
    "status": "completed",
    "task_name": "Analyze Harris County Jan 2025"
  },
  {
    "id": 4002,
    "parent_task_id": 4001,
    "agent_type": "research",
    "status": "completed",
    "task_name": "Fetch liens for county 5"
  }
]
```

### 9.4 Get Episode Events (Timeline)
**GET** `/episodes/{episode_id}/events`

**Query params**
- `event_types` (multi) – `llm_call`, `tool_event`, `decision`, `memory`
- `task_id` (optional)

**Response 200**
```json
[
  {
    "event_id": 1,
    "event_type": "llm_call",
    "created_at": "2025-11-21T06:00:05Z",
    "agent_task_id": 4001,
    "summary": "Orchestrator: plan analysis steps",
    "llm_call_id": 7001,
    "decision_id": null
  },
  {
    "event_id": 2,
    "event_type": "decision",
    "created_at": "2025-11-21T06:00:10Z",
    "agent_task_id": 4001,
    "summary": "Select top 50 candidate liens",
    "llm_call_id": 7002,
    "decision_id": 8001
  }
]
```

### 9.5 Get LLM Call Detail
**GET** `/llm-calls/{call_id}`

**Roles:** `dev`, `compliance`, `analyst` (content visibility may differ by role and settings).

**Response 200**
```json
{
  "id": 7001,
  "episode_id": 10001,
  "agent_task_id": 4001,
  "model_name": "gpt-5.1",
  "created_at": "2025-11-21T06:00:05Z",
  "prompt": "...possibly redacted...",
  "response": "...possibly redacted...",
  "prompt_tokens": 1024,
  "response_tokens": 256,
  "temperature": 0.2,
  "top_p": 1.0,
  "tool_calls": [],
  "latency_ms": 850
}
```

### 9.6 Get Decision Detail
**GET** `/decisions/{decision_id}`

**Response 200**
```json
{
  "id": 8001,
  "episode_id": 10001,
  "agent_task_id": 4001,
  "decision_type": "select_top_deals",
  "impact_summary": "Selected 50 candidate liens from 1200 scraped records",
  "decision_payload": {
    "selected_lien_ids": [1001, 1002]
  },
  "created_at": "2025-11-21T06:00:10Z",
  "llm_call_id": 7002
}
```

### 9.7 LLM Calls Catalog
**GET** `/llm-calls`

Query by:
- `date_from`, `date_to`
- `model_name`
- `agent_type`
- token/latency ranges

Returns paginated list of calls with summary fields.

### 9.8 Decisions Catalog
**GET** `/decisions`

Query by:
- `decision_type`
- `agent_type`
- `date_from`, `date_to`

Returns paginated list of decisions with summaries.

### 9.9 Entities Search & Detail
**GET** `/entities/search`

Query param `q` matches liens, properties, investors, analysis runs.

**GET** `/entities/{entity_type}/{entity_id}`

Returns entity summary + related episodes & decisions.

### 9.10 Reasoning Settings
**GET** `/settings`
**PATCH** `/settings`

**Response 200**
```json
{
  "store_full_prompts": false,
  "store_redacted_prompts": true,
  "store_full_responses": false,
  "store_embeddings_only": true,
  "log_retention_days": 90
}
```

PATCH body uses same schema; backend persists and applies.

---
## 10. Health & Misc

### 10.1 Health Check
**GET** `/health`

**Response 200**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### 10.2 Readiness/Dependencies
**GET** `/health/ready`

Includes DB/Redis/LLM dependency checks.

---
## 11. Notes for Codex Agent

- Implement the API layer following this spec, using FastAPI route modules grouped by feature.
- Input/output schemas should be defined via Pydantic models matching the shapes above.
- All business rules, validation constraints, and status transition rules are defined in a separate **Business Rules & Validation Spec** document and must be enforced in services, not only at the DB level.
- The Reasoning Explorer endpoints are read-only and must enforce role-based access (`dev`, `compliance`, `analyst`), with content redaction behavior controlled via the `/settings` configuration.


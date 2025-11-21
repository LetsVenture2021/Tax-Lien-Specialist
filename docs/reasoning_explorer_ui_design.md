# Reasoning Explorer UI – Design Spec

Purpose: A web-based internal tool for developers, auditors, and compliance teams to inspect **AGI episodes**, **LLM calls**, **tool events**, and **decision traces** for the Tax Lien Strategist App.

---
## 1. High-Level Goals

- Provide **end-to-end visibility** from:
  - Lien / deal → Analysis run → Agent tasks → Episodes → LLM calls → Tool events → Decisions → Data changes
- Enable **debugging**, **compliance review**, and **post-mortems** for AGI behavior.
- Maintain a UX that is:
  - Filterable, searchable, and fast on large datasets
  - Readable for non-engineers (e.g., compliance officers)
  - Safe (with redaction options for sensitive content)

---
## 2. IA (Information Architecture)

### 2.1 Main Sections

**Global navigation (left sidebar):**
1. **Episodes** – Browse and filter agent episodes
2. **LLM Calls** – Raw prompt/response inspection
3. **Decisions** – High-level decision timeline view
4. **Entities** – Jump from lien/property/investor to related reasoning
5. **Settings** – Redaction, retention, access control toggles

---
## 3. Primary Screen: Episode Detail View

### 3.1 Layout Overview

**Three-column layout**:

- **Left Column – Episode & Task Tree**
  - Episode summary & metadata
  - Hierarchical task tree

- **Center Column – Timeline & Reasoning**
  - Time-ordered timeline of LLM calls, tool events, decisions

- **Right Column – Context & Metadata**
  - Entity context (lien, property, county, investor)
  - Memory snapshots
  - Links to OLTP data and metrics

### 3.2 Left Column – Episode & Task Tree

**Components:**
- Episode header card:
  - Episode ID / UUID
  - Agent type (Orchestrator / Research / Underwriting / Document)
  - Status (Running / Completed / Failed)
  - Start / end timestamps
  - Duration

- Task tree view:
  - Root: `root_task_id`
  - Children: all `agent_tasks` with `parent_task_id` references
  - Show status badges on tasks (pending, in_progress, completed, failed)
  - Click on a task to filter center timeline to events for that task

**Filters:**
- Agent type (multi-select)
- Status
- Date range

### 3.3 Center Column – Timeline & Reasoning

**Timeline view (vertical):**
- Each item = one of:
  - LLM call
  - Tool event
  - Decision event
  - Memory write

**Item types & visuals:**
- LLM call → chat bubble style:
  - Prompt (truncated) with “View full prompt” expand
  - Response (truncated) with “View full response” expand
  - Model name, temperature, latency
- Tool event → pill/card:
  - Tool name, status icon, duration
  - Input/Output JSON (collapsible)
- Decision event → badge + text:
  - `decision_type`
  - Short impact_summary
  - Link to details
- Memory write → subtle card:
  - memory_type (episodic/semantic/working)
  - importance_score
  - content excerpt

**Controls:**
- Toggle switches:
  - [x] Show LLM Calls
  - [x] Show Tool Events
  - [x] Show Decisions
  - [ ] Show Memory Writes
- Text search on:
  - Prompt content
  - Response content
  - Decision type

### 3.4 Right Column – Context & Metadata

**Panels:**

1. **Entity Context Panel**
   - If episode is tied to `analysis_run_id`:
     - Show run details: type, county, timestamp, status
   - If associated with lien/property:
     - Lien ID, property address, county
     - Quick metrics: LTV, yield, risk score
   - Links:
     - “View in Deal Console” (links to main app)

2. **Memory Panel**
   - List of top-N `ai_agent_memories` for this episode sorted by importance
   - Click to highlight related timeline events

3. **Metadata Panel**
   - Model version
   - Namespace (prod/test/experiment)
   - Prompt redaction status
   - Flags (e.g., `high_risk_decision`, `compliance_review_required`)

---
## 4. Episodes List View

### 4.1 Purpose

Quickly locate episodes by:
- Date range
- Agent type
- Status
- Involvement with a specific lien/property/investor

### 4.2 Layout

- **Top filter bar:**
  - Date range picker
  - Agent type dropdown
  - Status multi-select
  - Entity search (Lien ID / Property APN / Investor)

- **Table columns:**
  - Episode ID / UUID
  - Agent type
  - Status
  - Root task name
  - Related county / lien / analysis run
  - Started at
  - Duration
  - # LLM calls
  - # Decisions

- Row click → Episode Detail View

---
## 5. LLM Calls View

### 5.1 Purpose

Raw view over `ai_llm_calls` for debugging and performance optimization.

### 5.2 Layout

- Filter bar:
  - Date range
  - Model name
  - Agent type
  - Latency range
  - Token count range

- Table columns:
  - Call ID
  - Timestamp
  - Model
  - Agent type
  - Episode ID
  - Task name
  - Prompt tokens / Response tokens
  - Latency (ms)
  - # Tools called

- Row click → Slide-over / modal with:
  - Prompt text (redacted/hashed if configured)
  - Response text
  - Tool calls (links to `llm_tool_events`)
  - Quick tags: `has_error`, `has_tool_calls`, `long_latency`

---
## 6. Decisions View

### 6.1 Purpose

Top-down view of high-level decisions (e.g., "skip county", "promote deal", "reject deal").

### 6.2 Layout

- Filter bar:
  - Decision type dropdown
  - Agent type
  - Date range
  - County / Lien / Investor filters

- Table columns:
  - Decision ID
  - Decision type
  - Agent type
  - Episode ID
  - Task name
  - Impact summary
  - Created at

- Detail pane:
  - decision_payload JSON
  - Linked LLM call
  - Linked tool events
  - Linked entities (lien, property, analysis run)

---
## 7. Entities View

### 7.1 Purpose

Entry point for compliance: start from a **business entity** (lien, property, investor, analysis run) and then show **all relevant reasoning**.

### 7.2 Search & Detail

- Search card:
  - Input: lien ID / certificate number / property address / investor name / analysis_run_id

- On result selection:
  - Show summary of entity (e.g., property address & lien metrics)
  - Tabbed view:
    - **Episodes** – list of episodes touching this entity
    - **Decisions** – decisions referencing this entity
    - **Documents** – generated docs tied to entity
    - **Metrics** – key numeric metrics over time

---
## 8. Settings / Compliance Controls

### 8.1 Redaction & Retention

- Toggles / config:
  - [ ] Store full prompts
  - [x] Store redacted prompts (mask names, addresses, PII)
  - [ ] Store responses
  - [x] Hash prompts, keep only embeddings
- Retention rules:
  - LLM logs retention (e.g., 30 / 90 / 365 days)
  - Decision events retention

### 8.2 Access Control

- Role-based access:
  - `dev` – full raw access
  - `compliance` – redacted prompt view, full decisions
  - `analyst` – high-level summary only

---
## 9. UI Technology & Components (Recommended)

- **Frontend:** React + TypeScript + TailwindCSS
- **State Management:** React Query / TanStack Query
- **Charts/Timeline:** Recharts or VisX for event timeline
- **Layout:**
  - Left sidebar navigation
  - Three-column layout on Episode Detail

### Key Components

- `<EpisodeList />`
- `<EpisodeDetail />`
- `<TaskTree />`
- `<TimelineEvents />`
- `<LLMCallCard />`
- `<DecisionCard />`
- `<ToolEventCard />`
- `<MemoryPanel />`
- `<EntityContextPanel />`
- `<SettingsCompliancePanel />`

---
## 10. Example Routing Structure

- `/episodes`
- `/episodes/:episodeId`
- `/llm-calls`
- `/decisions`
- `/entities`
- `/settings`

---
## 11. Future Enhancements

- Diff view: compare two episodes or decisions side-by-side.
- Anomaly detection highlights: auto-flag episodes with unusual patterns (e.g., extremely high token usage, diverging decisions).
- Export bundles (JSON/PDF) for regulators or external auditors.

---
**End of Reasoning Explorer UI Design Spec**


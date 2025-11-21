# Reasoning Explorer – User Stories & Acceptance Criteria

Product: **Reasoning Explorer UI** for the Tax Lien Strategist App (internal tool)
Users: **Developers**, **Compliance Officers**, **Data/ML Engineers**, **Product Owners**

---
## Epic 1: Browse & Filter Agent Episodes

### User Story 1.1 – List Episodes
**As a** developer or compliance officer  
**I want** to see a list of agent episodes with key metadata  
**So that** I can quickly find relevant reasoning flows to inspect.

**Acceptance Criteria:**
1. A page `/episodes` displays a paginated table of episodes.
2. Each row shows at least: Episode ID/UUID, agent type, status, root task name/ID, related county or analysis_run_id (if available), started_at, duration, and counts of LLM calls and decisions.
3. Clicking a row navigates to `/episodes/:episodeId` (Episode Detail View).
4. The table is sorted by `started_at` descending by default.
5. Empty state: if no episodes exist, show an informative message and not a blank table.

---
### User Story 1.2 – Filter Episodes
**As a** developer or compliance officer  
**I want** to filter episodes by key criteria  
**So that** I can narrow down to episodes of interest.

**Acceptance Criteria:**
1. The `/episodes` page includes a filter bar with:
   - Date range picker (applied to `started_at`)
   - Agent type multi-select (orchestrator, research, underwriting, document)
   - Status multi-select (running, completed, failed)
   - Free-text search field (searches Episode ID/UUID, root task name, related county name).
2. Changing filters updates the list without a full page reload.
3. When no results match the filter, an informative "No episodes found" message is shown.
4. Filter state is preserved when navigating into an episode and back using the browser back button.

---
## Epic 2: Inspect Episode Detail & Timeline

### User Story 2.1 – View Episode Summary & Task Tree
**As a** developer  
**I want** to see a summary of an episode and its task tree  
**So that** I understand how work was structured across agents.

**Acceptance Criteria:**
1. The page `/episodes/:episodeId` loads an Episode Detail View.
2. A header card shows: Episode ID/UUID, agent type, status, started_at, completed_at (if set), duration, related analysis_run_id (if any).
3. A tree view shows the root task and child tasks:
   - Node label displays task_name, agent_type, and status.
   - Clicking a task node filters the central timeline to events related to that task.
4. If an episode has no tasks, show a clear "No tasks recorded" message.

---
### User Story 2.2 – View Timeline of Events
**As a** developer or compliance officer  
**I want** to see a chronological timeline of events (LLM calls, tool events, decisions, memory writes)  
**So that** I can reconstruct what the AGI system did step by step.

**Acceptance Criteria:**
1. The center column shows a vertical timeline of events sorted by `created_at`.
2. Event types are visually distinct:
   - LLM calls (icon + label, e.g., "LLM CALL")
   - Tool events (icon + label, e.g., "TOOL")
   - Decision events (icon + label, e.g., "DECISION")
   - Memory writes (icon + label, e.g., "MEMORY")
3. Each event shows at minimum: type, timestamp, agent_task_id, and a short description (e.g., `decision_type` or tool_name).
4. There are toggle checkboxes to show/hide each event type; enabling/disabling updates the timeline immediately.
5. When a task is selected in the task tree, only events related to that task are shown; a clear indicator shows that a task filter is active, with a way to clear it.

---
### User Story 2.3 – Drill into LLM Calls
**As a** developer  
**I want** to drill into individual LLM calls  
**So that** I can inspect prompts, responses, parameters, and performance.

**Acceptance Criteria:**
1. Clicking a timeline event of type "LLM Call" opens a detail panel (modal or right-side drawer).
2. The detail panel includes:
   - model_name, timestamp
   - prompt_tokens, response_tokens
   - temperature, top_p, latency
   - truncated prompt text with a “View full prompt” expand option
   - truncated response text with a “View full response” expand option
   - tool_calls JSON (if any) formatted in a readable way.
3. There is a visible warning or redaction badge if prompts/responses are partially masked per settings.
4. Closing the panel returns the user to the same scroll position in the timeline.

---
### User Story 2.4 – Inspect Tool & Decision Events
**As a** developer or compliance officer  
**I want** to inspect tool calls and decisions  
**So that** I can understand how the system used tools and changed state.

**Acceptance Criteria:**
1. Clicking a "Tool Event" opens a detail panel showing:
   - tool_name, status, timestamp
   - tool_input JSON
   - tool_output JSON
   - error_message (if status = failed)
2. Clicking a "Decision Event" opens a detail panel showing:
   - decision_type
   - impact_summary
   - decision_payload JSON
   - link to the originating LLM call (if any) which, when clicked, opens the LLM Call detail.
3. For failed tool events or unusual decisions, a distinct style (e.g., warning color) is used.

---
## Epic 3: Entity-Centric Reasoning Inspection

### User Story 3.1 – Search by Business Entity
**As a** compliance officer  
**I want** to search reasoning by lien, property, investor, or analysis run  
**So that** I can review everything the AGI did related to a specific real-world entity.

**Acceptance Criteria:**
1. The `/entities` view provides a search input that accepts:
   - Lien ID / certificate number
   - Property APN or address text
   - Investor display_name
   - analysis_run_id
2. Search results show a list of matching entities with basic details (e.g., address, county for properties; name for investors).
3. Selecting an entity shows a detail page with at least:
   - Summary card of the entity (key properties)
   - Tabs for: Episodes, Decisions, Documents, Metrics.
4. The "Episodes" tab lists all related episodes, clicking one opens Episode Detail View.
5. The "Decisions" tab lists decisions whose payload references this entity.

---
## Epic 4: LLM Calls & Decisions Catalog

### User Story 4.1 – LLM Calls Catalog
**As a** developer or ML engineer  
**I want** a catalog of LLM calls  
**So that** I can analyze performance, token usage, and anomalies.

**Acceptance Criteria:**
1. The `/llm-calls` page shows a paginated table over `ai_llm_calls`.
2. Filters include:
   - Date range
   - Model name
   - Agent type (via join to agent_tasks)
   - Latency range
   - Prompt/response token range
3. Each row shows: call ID, timestamp, model_name, episode_id, agent_type, task_name (if available), latency, prompt_tokens, response_tokens, # tool calls.
4. Clicking a row opens the same LLM Call detail panel as in Episode Detail.

---
### User Story 4.2 – Decisions Catalog
**As a** compliance officer  
**I want** a view of all high-level decisions  
**So that** I can monitor and audit AGI-driven changes.

**Acceptance Criteria:**
1. The `/decisions` page shows a paginated table over `ai_llm_decision_events`.
2. Filters include:
   - Decision type
   - Agent type
   - Date range
   - County / lien ID / investor (via entity joins or text search on payload)
3. Each row shows: decision ID, decision_type, episode_id, task_name (if available), impact_summary, created_at.
4. Clicking a row opens a detail panel showing decision_payload JSON, links to related LLM call, and links to entity detail pages.

---
## Epic 5: Compliance & Redaction Controls

### User Story 5.1 – Configure Redaction & Retention
**As a** compliance admin  
**I want** to configure how much LLM content is stored and for how long  
**So that** we can comply with privacy and regulatory requirements.

**Acceptance Criteria:**
1. The `/settings` page is only accessible to users with the `compliance` or `admin` role.
2. The page shows toggles/options for:
   - Store full prompts (on/off)
   - Store redacted prompts (on/off)
   - Store full responses (on/off)
   - Keep only embeddings (on/off)
   - LLM log retention period (dropdown or numeric days)
3. Changing settings triggers an update via backend API; success/failure status is displayed.
4. Active settings state is reflected in the Episode and LLM Call detail views (e.g., redaction badge).

---
## Epic 6: Access Control & Roles

### User Story 6.1 – Role-Based UI Behavior
**As a** system owner  
**I want** role-based access in the Reasoning Explorer  
**So that** users only see what they are authorized to see.

**Acceptance Criteria:**
1. At least three roles are recognized in the UI for this tool: `dev`, `compliance`, `analyst`.
2. `dev` role:
   - Can access all views and see full prompts/responses (subject to global settings).
3. `compliance` role:
   - Can access all views.
   - Prompts/responses appear redacted if redaction is enabled.
   - Can change settings on `/settings`.
4. `analyst` role:
   - Can view Episodes, Decisions, and Entities.
   - Cannot access `/settings`.
   - May be restricted to summary-level info (e.g., hides raw prompt text if configured).
5. Unauthorized access attempts (e.g., analyst opening `/settings`) result in a friendly error/redirect.

---
## Epic 7: Performance & UX

### User Story 7.1 – Responsive Timeline & Pagination
**As a** frequent user of the Reasoning Explorer  
**I want** the UI to remain responsive even with large numbers of events  
**So that** I can work efficiently.

**Acceptance Criteria:**
1. Episode timeline uses virtualized rendering for large event lists (e.g., 1,000+ events) to avoid UI lag.
2. Pagination or lazy-loading is applied where appropriate (episodes list, LLM calls catalog, decisions catalog).
3. API calls are debounced where filters are updated rapidly (e.g., typing in search fields).
4. Loading states (spinners/skeletons) are visible while data is being fetched.

---
## Definition of Done (for the Reasoning Explorer Feature)

- All user stories above have passing acceptance criteria.
- Role-based access is enforced both in frontend and backend.
- UI has basic styling consistent with the main admin/dev tools (no raw, unstyled HTML).
- Core flows are covered by integration tests (e.g., episode listing, detail, LLM call drilldown).
- Performance smoke test done with a dataset containing at least:
  - 10,000 episodes
  - 100,000 LLM calls
  - 50,000 decision events
- Documentation exists for:
  - How to access the Reasoning Explorer
  - How to interpret episodes, events, and decisions
  - How redaction and retention settings work.

---
**End of User Stories & Acceptance Criteria**


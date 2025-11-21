# Business Rules & Validation Specification – Tax Lien Strategist + AGI / Reasoning Explorer

Version: v1  
Audience: GPT‑5.1 Codex Agent, backend engineers, QA

This document defines **domain rules and validation constraints** for core entities and workflows. It complements the **Backend API Specification** and must be enforced primarily in the **service layer**, with DB constraints as an additional safety net.

---
## 0. General Validation Conventions

### 0.1 Identity & Keys
- Primary keys: integer IDs, auto-increment.
- External references (e.g., `certificate_number`, `apn`) are strings with uniqueness constraints per relevant scope (e.g., per county).

### 0.2 Money & Percentages
- All monetary values are stored as **integers in cents** or **DECIMAL(18,2)** (decision left to implementation, but must be consistent across the app).
- Interest and yield rates are stored as **decimal fractions** (e.g., 18% → `0.18`).
- Validation:
  - Interest/yield rates must be between `0` and `1` (0–100%) inclusive, unless explicitly documented otherwise.
  - LTV (loan-to-value) ratios must be between `0` and `1`.

### 0.3 Dates & Time
- All timestamps are UTC ISO 8601.
- Date fields without time (e.g., `auction_date`) should be normalized to UTC midnight where needed.
- Validation:
  - `redemption_date` > `auction_date` when both exist.
  - `acquired_date` ≥ `auction_date`.
  - `created_at` ≤ `updated_at` (if both exist; updated_at may initially equal created_at).

### 0.4 Status Fields
- All status fields use **enumerated strings** validated strictly against known sets.
- Invalid or unknown statuses MUST be rejected at the service layer with a 400 error.

---
## 1. Investors & Investor Profiles

Entities:
- `Investor` (legal entity or person)
- `InvestorProfile` (risk/return preferences)

### 1.1 Investor

Fields & validation:
- `display_name` (string, required)
  - 3–200 characters.
- `email` (string, required for digital clients)
  - RFC-compliant email.
- `phone` (string, optional)
- `status` (enum)
  - `active`, `inactive`, `archived`.
  - Default: `active`.

Allowed transitions:
- `active` → `inactive` or `archived`.
- `inactive` → `active`.
- `archived` is terminal (no reactivation without admin override; by default disallow).

Business rules:
- An `archived` investor:
  - Cannot create new portfolios.
  - Cannot be assigned new holdings or analysis runs.

### 1.2 Investor Profile

Fields (simplified):
- `risk_tolerance` (enum): `conservative`, `moderate`, `aggressive`.
- `target_yield_min` (decimal fraction): 0–1.
- `target_yield_max` (decimal fraction): 0–1, and `target_yield_max` ≥ `target_yield_min`.
- `max_single_lien_exposure` (decimal fraction): 0–1 (max percentage of portfolio capital in a single lien).
- `max_county_exposure` (decimal fraction): 0–1.
- `max_budget` (decimal, optional): If present, > 0.

Business rules:
- `conservative` profiles should usually have:
  - `target_yield_max` ≤ 0.15 by default (Codex may expose configuration to override).
- `aggressive` profiles may have higher yield targets but must not exceed 1.0.

---
## 2. Properties

### 2.1 Property Core Fields

- `address` (string, required): 5–255 characters.
- `city` (string, required): 2–100 characters.
- `state` (string, required): US state code (2-letter, e.g., `TX`).
- `zip` (string, optional but recommended): 5 or 9 digits.
- `county_id` (FK to County, required for lien‑backed assets).
- `apn` (string, optional but unique per county if present).
- `property_type` (enum): `SFR`, `MFR`, `Land`, `Commercial`, `Other`.

Validation:
- `county_id` must reference an active county.
- `apn` uniqueness enforced per (`county_id`, `apn`).

### 2.2 Property Valuations

Fields:
- `value` (decimal): > 0.
- `as_of` (timestamp, required).
- `method` (enum): `AVM`, `BPO`, `Appraisal`, `TaxAssessed`, `Other`.
- `source` (string): free-text (max 100 chars).

Business rules:
- Each property may have multiple valuations; there is exactly one **current valuation** defined as the valuation with the latest `as_of` <= now.
- If valuations tie on `as_of`, the one with the **highest trust score** (if implemented) or latest `created_at` wins.

---
## 3. Counties & County Rules

### 3.1 County

Fields:
- `name` (string, required).
- `state` (2-letter code, required).
- `auction_type` (enum): `tax_lien`, `tax_deed`, `hybrid`.
- `redemption_period_months` (integer): ≥ 0.
- `max_interest_rate` (decimal fraction): 0–1.

Business rules:
- For `tax_lien` counties, at least one of `interest_rate`, `penalty_rate` or a lookup schedule must be defined.
- For `tax_deed` counties, liens may not be created; instead, a separate flow may be used (out of scope unless implemented).

---
## 4. Liens

### 4.1 Lien Core Fields

- `certificate_number` (string, required)
  - Unique per county.
- `county_id` (FK, required).
- `property_id` (FK, required).
- `face_value` (decimal): > 0.
- `interest_rate` (decimal fraction): 0–1.
- `penalty_rate` (decimal fraction, optional): 0–1.
- `auction_date` (date/timestamp, required).
- `redemption_date` (date/timestamp, optional).
- `status` (enum):
  - `available` – not yet acquired by the investor/fund.
  - `acquired` – purchased and held.
  - `redeemed` – redeemed by property owner.
  - `defaulted` – went to deed / non-redeemed status.
  - `written_off` – written off for accounting reasons.

Validation:
- `face_value` must be > 0.
- `interest_rate` must be <= county `max_interest_rate` if such a limit exists.
- `redemption_date` (if present) must be ≥ `auction_date`.

### 4.2 Lien Status Transition Rules

Valid transitions:
- `available` → `acquired`
- `acquired` → `redeemed` or `defaulted` or `written_off`
- `redeemed` → `written_off` (accounting cleanup only)
- `defaulted` → `written_off` (accounting cleanup only)

Disallowed transitions (examples):
- `redeemed` → `acquired`
- `written_off` → any other status

Business rules:
- When transitioning to `acquired`, the following must be provided:
  - `investor_id` or `portfolio_id` (depending on design).
  - `acquired_date` (≥ `auction_date`).
- When transitioning to `redeemed`:
  - `redemption_date` must be provided and ≥ `auction_date`.
  - Redemption proceeds must be computed or enqueued for computation.
- When transitioning to `defaulted`:
  - Mark downstream flows to track potential deed acquisition or loss.

---
## 5. Deal Metrics & Yield Calculations

### 5.1 Basic Yield Formula (Simple)

For a redeemed lien:

- Inputs:
  - `face_value` (FV)
  - `interest_rate` (r, decimal fraction)
  - `days_held` (d)
- Simple interest assumption:

```text
accrued_interest = FV * r * (d / 365)

gross_proceeds = FV + accrued_interest

yield = accrued_interest / FV
```

Validation:
- `days_held` >= 0.
- `yield` must be between 0 and 1 for reporting; if higher, flag as anomalous in logs.

### 5.2 Risk-Adjusted Score (Example)

Each lien can have a **risk_score** between 0 and 1 (0 = low risk, 1 = high risk).  
Deal score example:

```text
deal_score = w_yield * normalized_yield + w_risk * (1 - risk_score) + w_ltv * (1 - ltv)
```

Where:
- `normalized_yield` is yield scaled to 0–1 based on investor profile targets.
- Weights `w_yield`, `w_risk`, `w_ltv` sum to 1.

Validation:
- All inputs must be in 0–1 range.
- Sum of weights must be 1; otherwise, reject configuration.

Codex should implement weights as **configurable constants** (e.g., from environment or config file), not hard-coded magic numbers.

---
## 6. Analysis Runs & Constraints

### 6.1 Analysis Run Inputs

From API spec `POST /analysis/runs` and `/agents/orchestrator/analysis`.

Validation:
- `county_id` must reference an active county.
- `investor_profile_id` must be active.
- `max_budget` must be > 0.
- `target_yield_min` must be between 0 and 1.
- `constraints.max_ltv` must be between 0 and 1 if provided.

### 6.2 Candidate Selection Rules

At a minimum:
- Exclude liens where `status != available`.
- Exclude liens that violate investor profile constraints:
  - LTV > `max_ltv` (if property valuation available).
  - Yield below `target_yield_min` (if computable).
- Exclude liens in counties not allowed by profile (if such a restriction is added later).

### 6.3 Budget & Diversification Rules

For a given analysis run:
- Total `investment_amount` of **selected** deals must not exceed `max_budget`.
- Per-lien exposure:
  - `investment_amount` / `max_budget` ≤ `max_single_lien_exposure` (from profile).
- Per-county exposure:
  - Sum of `investment_amount` per county / `max_budget` ≤ `max_county_exposure`.

If constraints cannot be satisfied with available liens, orchestrator should:
- Prefer solutions that maximize yield while remaining under budget.
- If no feasible solution exists, return a clear status and summary in the analysis run:
  - `status`: `completed_no_feasible_solution`.

---
## 7. Portfolios & Holdings

### 7.1 Portfolio

Fields:
- `name` (string): 3–200 characters.
- `investor_id` (FK, required).
- `base_currency` (enum/string): e.g., `USD`.

Rules:
- An investor may have multiple portfolios.
- A portfolio may be **closed**; in that state, no new holdings can be added.

### 7.2 Holdings

- Each holding links a `portfolio` with one `lien`.
- `investment_amount` must be > 0 and ≤ `lien.face_value`.
- `acquired_date` ≥ `lien.auction_date`.
- `status` (enum): `active`, `redeemed`, `defaulted`, `sold`, `written_off`.

Transitions:
- `active` → `redeemed`/`defaulted`/`sold`/`written_off`.
- Non-active statuses are terminal for that holding.

NAV calculation:
- NAV = sum of book value + accrued interest (if recognized) – write-downs.
- Codex should implement NAV as a **service-layer calculation**, not stored directly; if stored for caching, mark it with an `as_of` timestamp.

---
## 8. Documents & Notifications

### 8.1 Documents

- A document must be associated with at least one entity: `lien`, `property`, `portfolio`, `analysis_run`, or `investor`.
- `storage_uri` or `blob_key` must be non-empty.
- When generating a document via agent:
  - The generation job must verify that referenced entities exist.
  - On failure, mark document as `failed` with a clear error message.

### 8.2 Notifications

- Notifications must have:
  - `recipient_user_id` (FK) OR `recipient_email`.
  - `type` (enum): e.g., `system_alert`, `analysis_complete`, `document_ready`.
  - `status`: `pending`, `sent`, `failed`, `read`.

Validation:
- `pending` → `sent` or `failed`.
- `sent` → `read`.
- `failed` should never transition back to `pending` without explicit retry logic.

---
## 9. AGI / Agentic Layer – Behavioral Rules

These rules constrain how agents are allowed to behave and log.

### 9.1 Orchestrator Agent

- Must:
  - Respect investor profile constraints when calling tools.
  - Never commit state changes (e.g., portfolio modifications) without explicit confirmation steps in code.
- Orchestrator can:
  - Create `analysis_runs`.
  - Enqueue tool calls for research and underwriting.
  - Propose decisions, which are then persisted by the service layer.

### 9.2 Research Agent

- May call tools to:
  - Fetch county lien lists.
  - Fetch property data.
  - Retrieve historical performance metrics.
- Must:
  - Record each tool call as a `tool_event` in `ai_llm_tool_events`.

### 9.3 Underwriting Agent

- Computes metrics and proposes risk scores.
- Must:
  - Not directly modify holdings/portfolios.
  - Only propose actions via decision payloads.

### 9.4 Document Agent

- Generates summaries, memos, and investor-facing documents.
- Must:
  - Use redacted data where required.
  - Never include raw PII that has been marked for redaction.

---
## 10. Logging, Redaction & Reasoning Rules

### 10.1 LLM Logs

- Every LLM call must be logged in `ai_llm_calls` with:
  - `episode_id` (if applicable), `agent_task_id`, `model_name`, timestamps, token counts, latency.
- `prompt` and `response` content:
  - Must be **redacted** according to the **Prompt Library & Redaction Rules** document before persistence, based on current `/settings`.

### 10.2 Redaction Rules (High-Level)

- PII to redact (at minimum):
  - Personal names (if external, not internal staff or public figures).
  - Personal phone numbers, emails, SSNs, bank account numbers.
  - Exact property addresses for non-public datasets (implementation detail can vary).

- Redaction format:
  - Replace sensitive spans with `[REDACTED:<TYPE>]`, e.g., `[REDACTED:EMAIL]`.

### 10.3 Reasoning Explorer Access

- Roles:
  - `dev`, `compliance`, `analyst` may access.
- Content visibility:
  - `dev`: may see more detail but still respects core redaction rules.
  - `compliance`: must see enough to audit but still respect PII removal policies.
  - `analyst`: may see higher-level summaries and structured payloads but not full raw prompts if disallowed by settings.

---
## 11. Error & Edge Case Handling

### 11.1 County Data Missing

- If property or county data is insufficient to compute a metric:
  - Mark metric as `null` and include an explanation field (e.g., `missing_property_valuation`).
  - Do **not** guess values.

### 11.2 LLM Failure / Rate Limits

- On LLM failure:
  - Retry with exponential backoff up to N times (configurable, default 3).
  - If still failing, record a decision/event with status `failed_llm_call` and expose this status in the Reasoning Explorer.

### 11.3 Conflicting Investor Constraints

- If investor profile constraints are mutually incompatible (e.g., `target_yield_min` too high given risk_tolerance and max_ltv):
  - Mark analysis run with status `invalid_profile_constraints`.
  - Provide a human-readable explanation.

---
## 12. Notes for Codex Agent

- Enforce these rules in the **service layer** (e.g., `*_service.py`) and use Pydantic models for request validation where applicable.
- Use DB-level constraints for key integrity and uniqueness, but never rely solely on them for domain rules.
- When a rule is violated, return a 400 error with `code` field indicating the rule, e.g., `"INVALID_STATUS_TRANSITION"`, `"YIELD_OUT_OF_RANGE"`, `"BUDGET_EXCEEDED"`.
- Keep all magic numbers (weights, thresholds) in a **central config** module or environment variables to allow tuning without code changes.


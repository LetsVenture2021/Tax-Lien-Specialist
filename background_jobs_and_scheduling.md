# Background Jobs & Scheduling Specification – Tax Lien Strategist + AGI / Reasoning Explorer

Version: v1  
Audience: GPT‑5.1 Codex Agent, backend engineers, DevOps / SRE

This document defines all recurring and on-demand background jobs used by the Tax Lien Strategist application. Jobs may run via **Celery**, **RQ**, or **Cloud‑native schedulers** (Azure Functions Timer Triggers, GCP Cloud Scheduler). The Codex Agent should implement a consistent job layer (recommended: Celery + Redis) unless the deployment plan mandates otherwise.

Each job definition includes:
- Description
- Trigger type (cron/scheduled, event-based, manual)
- Inputs
- Outputs
- Idempotency rules
- Error handling & retries
- Logging requirements
- Downstream side-effects

---
# 1. Scheduler Overview

Two categories of jobs exist:

### **1. Recurring Scheduled Jobs (CRON-like)**
Executed on schedule—daily, hourly, or weekly. Examples:
- County lien ingestion
- Valuation refresh
- Reasoning log cleanup
- Portfolio NAV refresh (optional)

### **2. Event-Driven Jobs**
Triggered by API actions or internal agent flows. Examples:
- Start analysis run
- Generate documents
- Compute deal metrics
- Persist LLM decisions

Both types must be visible in:
- `/api/admin/jobs` (optional admin endpoint)
- System logs (structured JSON)
- Application Insights / Cloud Monitoring dashboards

---
# 2. Core Job Definitions (High Priority)

## **2.1 County Lien Ingestion Job**
**ID:** `ingest_county_liens`  
**Trigger:** Scheduled (daily at 02:00 local) + Manual  
**Inputs:** `county_id`, optional date range  
**Outputs:** New or updated lien records  
**Description:** Fetch lien availability from county data sources, API endpoints, CSVs, or scraping pipelines.

### Rules:
- Idempotent: running twice should not create duplicate liens.
- Validate lien fields against county rules.
- Log each ingestion summary:
  - total retrieved
  - created
  - updated
  - failed (with reasons)
- If scraping fails:
  - Retry 3 times with exponential backoff.
  - After 3 failures: log job failure and send a system notification.

---
## **2.2 Property Valuation Refresh Job**
**ID:** `refresh_property_valuations`  
**Trigger:** Scheduled (daily at 03:00 local)  
**Inputs:** none (or explicit property_id)  
**Outputs:** New valuations inserted into `property_valuations`

### Rules:
- Fetch valuations via AVM providers or internal models.
- If valuation drops more than X% from last value (configurable), flag anomaly.
- On failure to fetch valuation:
  - Mark as missing and continue.

---
## **2.3 Portfolio NAV Recalculation Job**
**ID:** `recalculate_portfolio_nav`  
**Trigger:** Daily at 04:00  
**Inputs:** optional `portfolio_id`  
**Outputs:** Updated NAV entries (cached or stored with timestamp)

### Rules:
- NAV = sum of holdings’ book value + accrued interest – write-downs.
- For incomplete valuation data, mark NAV as partial.

---
## **2.4 Reasoning Log Cleanup Job**
**ID:** `cleanup_reasoning_logs`  
**Trigger:** Daily at 01:00  
**Inputs:** none  
**Output:** Deleted or archived old logs

### Rules:
- Reads `/settings.log_retention_days`.
- Purges:
  - `ai_llm_calls`
  - `ai_agent_episodes`
  - `ai_agent_memories`
  - `ai_llm_tool_events`
  - `ai_llm_decision_events`
- Optionally archives to blob storage before deletion.
- Must be idempotent.

---
# 3. Analysis Jobs

## **3.1 Start Analysis Run Job**
**ID:** `run_analysis`  
**Trigger:** Event-driven from `/analysis/runs` API or `/agents/orchestrator/analysis`.

### Inputs:
```json
{
  "analysis_run_id": 501
}
```

### Steps:
1. Load analysis run definition.
2. Validate investor constraints.
3. Fetch available liens for county.
4. Compute metrics (yield, LTV, risk score).
5. Filter against investor rules.
6. Generate candidate deals.
7. Persist summary & status.

### Rules:
- Must log agent episode if orchestrator is used.
- On any irreversible failure:
  - Mark run as `failed`.
  - Attach error summary.

### Retry:
- Up to 3 times for transient errors (LLM outage, DB timeout).

---
## **3.2 Compute Deal Metrics Job**
**ID:** `compute_deal_metrics`  
**Trigger:** Event-driven (part of analysis pipeline)  
**Inputs:** `lien_id`, optional `analysis_run_id`  
**Outputs:** Metric objects (yield, score, risk)

### Rules:
- Requires latest property valuation.
- If missing valuation:
  - return metrics with `null` and explanation.
- Must follow formulas defined in Business Rules spec.

---
## **3.3 Apply Deal Decisions Job**
**ID:** `apply_analysis_decisions`  
**Trigger:** Event-driven after user feedback or agent decisions  
**Inputs:** run ID, decision payload  
**Outputs:** updated deal statuses

### Rules:
- All decisions must be logged as `decision_events`.
- Deal status transitions must follow validation rules.
- Must be idempotent.

---
# 4. Document Jobs

## **4.1 Generate Document Job**
**ID:** `generate_document`  
**Trigger:** Event-driven via `/documents/generate`

### Steps:
1. Validate template exists.
2. Fetch context entities.
3. Call Document Agent.
4. Generate output PDF/HTML.
5. Store in blob storage.
6. Update DB record.
7. Notify user.

### Retry:
- 2 retries on LLM failure.

---
## **4.2 Archive Documents Job**
**ID:** `archive_old_documents`  
**Trigger:** Weekly schedule  
**Rule:** archive documents older than threshold.

---
# 5. Notification Jobs

## **5.1 Send Notification Job**
**ID:** `send_notification`  
**Trigger:** Event-driven when a notification is created

### Rules:
- Handles email/push/back-office notifications.
- On failed delivery:
  - Retry with exponential backoff.
  - After max retries: mark notification `failed`.

---
## **5.2 Digest Email Job**
**ID:** `send_digest_email`  
**Trigger:** Daily at 07:00  
**Output:** email summarizing notifications/updates

---
# 6. Reasoning Explorer Jobs

## **6.1 Index Reasoning Entities Job**
**ID:** `index_reasoning_entities`  
**Trigger:** Daily or on-demand  
**Description:** Updates search index for episodes, LLM calls, decisions, and tasks.

### Rules:
- Ensure embeddings are updated if using semantic search.

---
## **6.2 Archive Reasoning Data Job**
**ID:** `archive_reasoning_data`  
**Trigger:** Monthly  
**Output:** Transfer to cold storage

---
# 7. System & Maintenance Jobs

## **7.1 Database Backup Job**
Usually handled by cloud provider, but Codex must document fallback job if needed.

## **7.2 Rebuild Search Indices Job**
Rebuilds vector indexes or text indexes as needed.

## **7.3 Cleanup Temporary Files Job**
Cleans temp directories used by document generation.

---
# 8. Job Failure Semantics

### All jobs MUST:
- Log start and end (with duration).
- Log summary metrics.
- Log failures with complete stack traces.

### Retry Policy (default):
- Max retries: 3
- Backoff: exponential, jittered
- Fatal errors (bad input, validation error) should NOT retry.

---
# 9. Admin APIs for Jobs (Optional)
Codex should expose these endpoints if instructed:

### **GET /api/admin/jobs**
- Lists scheduled jobs and last run status.

### **POST /api/admin/jobs/{job_id}/run**
- Executes a job immediately.

---
# 10. Notes for Codex Agent
- Implement jobs in `backend/app/jobs/` with Celery tasks or equivalent.
- Group tasks logically (analysis, ingestion, documents, notifications).
- Ensure tasks are idempotent and log structured output.
- Use configuration values from environment variables for schedule times and retry counts.

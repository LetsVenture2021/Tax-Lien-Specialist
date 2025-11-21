# Implementation Index – Tax Lien Strategist

This index distills the specification corpus into domain-focused requirements. Use it as the working checklist while implementing the stack.

---
## Investors & Profiles

- **Data Model** (`data_model_tax_lien_strategist.md`, `database_schema_ddl.md`)
  - `users`, `investor_profiles`, `portfolios`, `portfolio_holdings` tables + status enums.
- **APIs** (`backend_api_specification.md` §1, §2, §7)
  - `/auth/*`, `/investors`, `/portfolios`, `/portfolios/{id}/holdings` (CRUD + archive flows).
- **Business Rules** (`business_rules_and_validation_spec.md` §1, §7)
  - Status transitions (`active`↔`inactive`, `archived` terminal), budgeting constraints, exposure limits, profile defaults.
- **Background Jobs** (`background_jobs_and_scheduling.md` §2.3)
  - `recalculate_portfolio_nav`, daily digest notifications, investor document workflows.
- **Agent Touchpoints** (`agent_protocol_and_tools.md`, `reasoning_explorer_*`)
  - Orchestrator enforces investor profile constraints; decisions logged via `log_decision_event`.

## Counties, Properties & Valuations

- **Data Model** (§2, §3 of data model)
  - `counties`, `properties`, `property_valuations`, `property_comps`, `auctions`.
- **APIs** (`backend_api_specification.md` §3–§4)
  - `/counties`, `/properties`, nested valuations endpoints, ingestion helpers.
- **Business Rules** (`business_rules_and_validation_spec.md` §2–§3)
  - Address validation, APN uniqueness, valuation freshness rules, county rate caps.
- **Background Jobs** (`background_jobs_and_scheduling.md` §2.1–§2.2)
  - `ingest_county_liens`, `refresh_property_valuations`.
- **Agent Touchpoints** (`agent_protocol_and_tools.md` §4)
  - Research agent `fetch_county_liens`, `fetch_property_details` tools; underwriting requires valuations.

## Liens & Deal Engine

- **Data Model** (§2.4, §4)
  - `liens`, `deal_metrics`, `risk_assessments`, `scenario_analyses`, `deal_scores`.
- **APIs** (`backend_api_specification.md` §4–§5)
  - `/liens`, `/liens/{id}/status`, `/analysis/runs`, metrics retrieval.
- **Business Rules** (`business_rules_and_validation_spec.md` §4–§6)
  - Status transition matrix, yield/LTV formulas, constraint enforcement, invalid solution handling.
- **Background Jobs** (`background_jobs_and_scheduling.md` §3)
  - `run_analysis`, `compute_deal_metrics`, `apply_analysis_decisions`.
- **Agent Touchpoints** (`agent_protocol_and_tools.md` §2–§4)
  - Orchestrator orchestrates analyses; Research gathers data; Underwriting computes metrics (`compute_lien_metrics`).

## Portfolios & Holdings

- **Data Model** (§5)
  - `portfolios`, `portfolio_holdings` with NAV-derived fields.
- **APIs** (`backend_api_specification.md` §7)
  - Portfolio CRUD, holdings management, NAV summaries.
- **Business Rules** (`business_rules_and_validation_spec.md` §7)
  - Holding status transitions, exposure calculations, NAV logic.
- **Background Jobs** (`background_jobs_and_scheduling.md` §2.3)
  - NAV recalculation, integration with notifications.
- **Agent Touchpoints**
  - Decisions originating from analyses update holdings via `apply_analysis_decisions`; logging in Reasoning Explorer ensures auditability.

## Documents & Notifications

- **Data Model** (§7–§8)
  - `documents`, `notifications`, `integration_events`, `audit_logs`.
- **APIs** (`backend_api_specification.md` §8–§9)
  - `/documents`, `/documents/generate`, `/notifications` endpoints.
- **Business Rules** (`business_rules_and_validation_spec.md` §8)
  - Storage URI requirements, notification status transitions, redaction obligations.
- **Background Jobs** (`background_jobs_and_scheduling.md` §4–§5)
  - `generate_document`, `archive_old_documents`, `send_notification`, `send_digest_email`.
- **Agent Touchpoints** (`agent_protocol_and_tools.md` §2.4, §4.4)
  - Document agent uses `generate_document_from_template`; notifications triggered post-generation.

## AGI Layer & Reasoning Explorer

- **Data Model** (§6, §8.2, Reasoning Explorer docs)
  - `agent_tasks`, `agent_logs`, `ai_agent_episodes`, `ai_llm_calls`, `ai_llm_tool_events`, `ai_llm_decision_events`, `embeddings`.
- **APIs** (`backend_api_specification.md` §10–§12)
  - `/agents/*`, `/admin/reasoning/v1/*` endpoints for episodes, calls, decisions, settings.
- **Business Rules** (`business_rules_and_validation_spec.md` §9–§10)
  - Logging completeness, redaction format, role-based visibility.
- **Background Jobs** (`background_jobs_and_scheduling.md` §2.4, §6)
  - Reasoning log cleanup, indexing, archival.
- **Agent Protocol** (`agent_protocol_and_tools.md`, `reasoning_explorer_*`)
  - Task lifecycle, tool catalog, safety constraints, structured decision logging.

## Infrastructure & DevEx

- **Stack Plans** (`azure_stack_and_deployment_plan_tax_lien_strategist.md`, `gcp_stack_and_deployment_plan_tax_lien_strategist.md`)
  - Service composition, environment variables, deployment targets.
- **CI/CD & Ops** (`ci_cd_pipeline_specification.md`, `logging_monitoring_and_slos.md`, `incident_response_runbooks.md`)
  - Pipeline stages, observability tooling, SLO metrics, on-call workflows.
- **Developer Workflow** (`local_development_guide.md`, `codex_build_instructions.md`)
  - Docker compose expectations, seed data process, step-by-step build roadmap.

---

## Open Questions / TODO Tracking

- Confirm monetary storage type (DECIMAL vs integer cents) across services.
- Validate full list of Reasoning Explorer tables from data model vs. logging docs before ORM implementation.
- Determine final set of optional admin endpoints (jobs, settings) after backbone is functional.

Update this index as specs evolve or clarifications are resolved.

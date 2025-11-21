# Tax Lien Strategist — AI-First Redesign Plan

## Vision
Create a focused Tax Lien Strategist product that:
- Produces fewer, higher‑quality leads (not a firehose).
- Keeps the investor in control while automating data collection, validation, strategy-specific analysis, outreach, and closing assistance.
- Uses explainable, auditable AI agents (RAG + tool use + verification pipelines) to reduce manual underwriting and improve conversion velocity.

## Guiding principles
- Human-in-the-loop: automation + guardrails; user finalizes offers and authorizes risky actions.
- Explainability: every AI recommendation has a retrievable rationale and source citations.
- Freshness and verification: prioritize live checks and signal confidence.
- Modularity: separate ingestion, enrichment, scoring, agent orchestration, UI, and integrations for independent iteration.

## Target users & workflows
- Small-medium investors focused on tax‑lien opportunities.
- Workflows: bulk lead upload → AI enrichment + dedupe + scoring → prioritized opportunity feed → strategy selection → automated outreach/campaigns → deal room + closing copiloted by agents.

## Core MVP features (priority)
1. Lead ingestion
   - CSV / Excel upload UI and API.
   - Public‑record ingestion stubs (county record ingestion pipeline to be implemented next).
2. Verification & enrichment
   - Owner match, title sanity checks, property status (tax status, pre-forfeiture), geocoding, basic skiptrace (phone/email).
   - Freshness checks (timestamped sources; re-verify on schedule).
3. Vectorization & similarity
   - Batch embeddings, store vectors in pgvector or a vector DB.
   - Similarity search (nearby historical comparable liens, similar owner notes).
4. Scoring & strategy analysis
   - Strategy templates (e.g., investor wants “fast flip”, “long term hold”, “redeem-only”).
   - Scoring engine combining rules + ML + LLM-based reasoning to produce recommended strategy and rank opportunities. Each recommendation includes an explainable reasoning block.
5. Reasoning Explorer & Deal Room
   - Page with LLM reasoning trace (short summary + sources).
   - Document store for property docs, tax records, offers, messages.
6. Campaign builder
   - AI‑generated direct‑mail / email / SMS templates tailored to property + owner + strategy.
   - Simple automation flows (send after N days, follow ups).
7. Celery (or Temporal) jobs for background processing
   - Embeddings, enrichment, verification, campaign scheduling.
8. Basic integrations
   - Email (SES), SMS (Twilio), optional dialer (SIP/Twilio), webhook for CRM export.
9. Audit & privacy
   - Action logging, AI prompt/response audit, data retention controls.

## Extended / Post-MVP features
- Continuous public-record ingestion connectors and county crawlers with change-tracking.
- Automatic opportunity discovery (scheduled ingestion + strategy-based matchers that push to user inbox).
- Agentic flows for contract generation, negotiation drafts, e-sign flow integration, and closing checklist automation.
- Multimodal analysis (OCR photos, tax bills, PDFs).
- Native marketing automations (segmentation, A/B testing, campaign analytics).
- Integrations with CRMs and transaction platforms.

## Architecture overview (high level)
- Frontend: React + TypeScript (Vite). Pages: Dashboard, Opportunities Feed, Upload, Deal Room, Reasoning Explorer, Campaign Builder, Settings.
- API: FastAPI (async) — auth (JWT / session), upload endpoints, lead endpoints, AI wrappers, webhooks.
- DB: PostgreSQL for relational data; pgvector extension or separate vector DB (Pinecone/Weaviate) depending on scale.
- Background: Celery (Redis broker) or Temporal as the orchestration engine for durable workflows.
- Message bus: Redis streams or Kafka for higher-scale ingestion pipelines.
- Storage: S3-compatible for documents.
- AI: LLM provider (OpenAI or private models) + embeddings. Retrieval layer for RAG. Agent orchestration layer to run tools (HTTP, DB, embed search, external APIs).
- External integrations: skiptrace, property vendors, county data APIs, Twilio, SMTP provider.
- Real-time: WebSocket / Server-Sent Events for live progress (uploads, agent runs).

## Key AI patterns
- Retrieval-Augmented Generation (RAG) — LLM answers cite source document IDs and confidence scores.
- Tool-using agents — agents can call:
  - embeddings search (vector store)
  - data enrichment tools (skiptrace, geocode)
  - DB read/write for stateful workflows
  - external APIs (mailing, SMS)
- Chain-of-thought capture — store agent reasoning summary plus top-K supporting documents.
- Vector scoring + rule ensembles — hybrid scoring combining heuristics, ML, and LLM explanations.

## Freshness & data quality strategy
- Source timestamping and provenance metadata on every record.
- Confidence scores per field (e.g., owner_email.confidence).
- Scheduled re-verification jobs (e.g., 7-day re-scan for high priority leads).
- Dedupe pipeline using fuzzy matching + embeddings for textual similarity.

## Data model sketch (key tables)
- properties (id, parcel_id, address, geo, last_seen, source, status)
- liens (id, property_id, lien_type, amount, tax_year, filing_date, source_payload)
- owners (id, property_id, name, contact_info[], source, last_verified)
- leads (id, property_id, owner_id?, uploaded_by, score, strategy_recommendation, reasoning_blob, status)
- embeddings (id, lead_id, vector, model, created_at)
- documents (id, lead_id, type, s3_url, ocr_text, created_at)
- campaigns, tasks, events, agent_runs (for audit)

## Example API endpoints (MVP)
- POST /api/v1/leads/upload — upload CSV / JSON list.
- POST /api/v1/leads/{id}/verify — enqueue verification job.
- GET /api/v1/opportunities — paginated ranked list with filters and sorting.
- POST /api/v1/opportunities/{id}/score — re‑score with a selected strategy.
- POST /api/v1/ai/respond — wrapper for generative tasks (summarize, suggest offer).
- POST /api/v1/ai/embeddings — batch embed texts.
- POST /api/v1/campaigns — create and start campaign.
- Webhook: /api/v1/webhooks/incoming (for provider callbacks).

## UI/UX components
- Dashboard: prioritized opportunities, pipeline health, scheduled re-verifications.
- Opportunities feed: configurable automation level (Manual / Assist / Auto), filters, confidence score, quick-actions (verify, create offer, push to campaign).
- Deal Room: timeline, documents, AI-suggested checklist, explainable strategy panel.
- Reasoning Explorer: view LLM chain of thought, source documents, adjust prompts and rerun.
- Campaign Builder: templates, AI variants, send-schedule, performance metrics.

## Security, compliance & privacy
- Sensitive data encryption at rest and in transit (S3/DB).
- Role-based access control (RBAC).
- PII minimization and retention policy (ability to scrub contact details).
- Audit trail for automated actions (who authorized what).

## Cost considerations
- LLM API usage (embedding and generation) will be a major recurring cost. Strategies:
  - batch embeddings off-peak and cache vectors.
  - use cheaper embedding models for indexing then heavier LLMs for on-demand reasoning.
  - allow self-hosted model option for enterprise customers.

## MVP timeline (example high-level)
- Week 0: finalize requirements + data contracts.
- Week 1–2: build upload API, CSV UI, storage, and basic leads CRUD.
- Week 3–4: implement enrichment worker: geocode + basic skiptrace + timestamping.
- Week 4–5: batch embeddings pipeline + vector store integration; simple similarity endpoint.
- Week 6–7: scoring engine (rules + LLM prompt for explainable summary).
- Week 8: opportunities feed UI + deal room basic view.
- Week 9: campaign builder (AI templates) + outbound integration (email).
- Week 10: polish, security review, deploy.

## Implementation notes / tech choices
- Vector store: start with Postgres + pgvector for MVP; consider Pinecone or Weaviate for scale.
- Orchestration: Celery is fine for MVP; use Temporal when you need durable orchestrations and better observability.
- LLMs: Start with OpenAI for speed in MVP; design abstraction layer to swap models.
- Observability: structured logging (structlog), tracing (OpenTelemetry).

## Next steps (developer actions)
- Create issue list (priority backlog) and map to milestones above.
- Implement the upload + embed + score pipeline as the first vertical feature (demoable).
- Build a Reasoning Explorer stub that shows prompt, LLM output, and sources.

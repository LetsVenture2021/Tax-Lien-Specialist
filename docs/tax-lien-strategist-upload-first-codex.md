```markdown
# Tax Lien Strategist — Upload-First AI Codex Redesign (Document-Centric & Real‑Time Lead Generation)

Summary
- Core idea: make the platform "upload-first" and "corpus-aware." User uploads + your enterprise document corpus become the canonical knowledge base the AI uses to clean, enrich, score, and generate tax‑lien opportunities in real time.
- Outcome: far fewer, higher‑quality leads (not a firehose). Real‑time opportunity generation, explainable underwriting, automated campaigns, and human-in-the-loop controls — all driven by typed codex functions and evidence-backed RAG.

Key new inputs accounted for
- User-provided CSV lead lists (many formats, large volumes).
- A high-value corpus of thousands of documents (deals, analyses, legal docs, templates, photos, PDFs).
- Need: automatic, repeatable, auditable transforms and live lead generation that leverages both uploaded lists and the document corpus.

Guiding principles
- Upload-first: every lead dataset uploaded is the canonical dataset for automation and model training.
- Corpus-backed reasoning: every AI recommendation cites supporting documents or uploaded lead rows.
- Hybrid automation: users choose Manual / Assist / Auto per workflow and per action.
- Freshness & verification: multi-source corroboration and active re-verification.
- Traceability: full transform, prompt, model-version, and evidence audit trail.

What "real-time lead generation" means here
- The system continuously monitors ingest sources (uploads, county feeds, webhooks), runs agentic enrichment pipelines, and can synthesize prioritized "opportunities" as soon as evidence crosses a configurable threshold.
- Generation uses: pattern detection in leads + corpus templates + RAG (e.g., detect a property with unpaid tax patterns, cross-check legal docs in corpus, create an opportunity with suggested strategy and campaign).
- Human-in-the-loop prevents undesired outbound actions; users approve before sends or offers (unless explicit auto mode is enabled).

Core components (expanded)
- Frontend: React (Vite) — Upload UI, Mapping Assistant, Opportunities Feed, Deal Room, Reasoning Explorer, Live Monitor view.
- API: FastAPI — typed endpoints for uploads, documents, codex-run, pipeline control, and real-time websockets.
- DB: PostgreSQL (relational) + pgvector or a managed vector DB. S3-compatible document storage.
- Background: Celery or Temporal for durable agent workflows and real-time orchestration.
- Document processing: OCR (Tesseract/Google OCR), PDF parsing, metadata extraction, named-entity extraction, embedding indexing.
- AI: LLMs for summarization/strategy/negotiation + embedding models for similarity; RAG retrieval layer, agent/tool layer for codex functions.
- Integrations: skiptrace providers, county APIs, Twilio, SES, DocuSign, CRM webhooks, SIP dialers (optional).

Codex functions (typed, agent-callable)
- ingest_upload(upload_id) — chunk, parse, map columns, store raw rows.
- suggest_mapping(sample_rows) — auto-suggest column mappings using corpus heuristics.
- clean_contacts(row) -> {phones[], emails[], confidence} — normalization + phone/email validation.
- normalize_address(row) -> {canonical_address, lat, lon, parcel_id?, confidence}
- enrich_public_records(row) -> {tax_status, liens[], filing_dates, source_refs}
- doc_corpus_lookup(query_or_embedding, top_k) -> [doc_refs with snippets + confidence]
- embed_text(text) -> vector
- dedupe_group(row_set) -> canonical_record_id
- segment_by_strategy(rows, user_profile) -> strategy_tags
- score_lead(row, strategy_profile) -> {score, band, reasoning, evidence_refs}
- synthesize_opportunity(canonical_record, evidence_refs, strategy) -> opportunity object + reasoning + required next steps
- start_monitor(rule, subscribers) -> create continuous agent to watch sources and push opportunities
- generate_campaign(lead, channel, tone) -> campaign_variants + subject-lines + proof-of-evidence
- outbound_send(action, requires_approval) -> schedules or sends (opt-in)
- explain_decision(opportunity_id) -> retrieval of chain-of-thought, prompts, and evidence

Document corpus usage
- Ingest all documents into document_corpus with OCR and metadata.
- Index corpus embeddings and expose retrieval endpoint used by codex functions.
- Use corpus as ground truth / precedent templates for contract generation, legal citations, underwriting heuristics, and scoring explanation examples.
- Allow training data extraction: label past deals to bootstrap ML scoring and calibrate LLM prompts.

Data model highlights (additions)
- uploads, upload_rows, transform_runs (function inputs/outputs/prompts)
- documents, document_corpus_embeddings
- canonical_leads, leads_evidence_links (link to upload_rows + documents)
- opportunities, opportunity_evidence, opportunity_confidence_history
- monitor_rules, agent_runs, campaign_variants, outbound_actions

Real-time & agent orchestration
- Monitor agents run as durable workflows:
  - Trigger sources: new upload, webhook county feed, scheduled county crawlers, document corpus change.
  - Agents run pipelines: ingest -> clean -> enrich -> embed -> score -> synthesize_opportunity.
  - When opportunity.score > threshold => create opportunity, notify user (WebSocket/email), attach evidence and explainable rationale.
- Streaming UX: WebSocket/SSE to show pipeline progress and live opportunities.

Quality & freshness improvements (innovations)
- Multi-source corroboration: require >= N independent signals (county record, corpus doc, last transaction) before labeling high-quality.
- Vector-backed dedupe + fuzzy business-name parsing to collapse LLC/Trust duplicates.
- Confidence-calibrated fields: each contact/address/filing date has a provenance list and confidence score.
- Scheduled re-verification and adaptive re-scoring (e.g., high-priority leads rechecked every 7 days).
- Active learning loop: user feedback on leads (accept/reject) used to update prompt templates and retrain scoring heuristics.

Explainability & audit
- Every AI output stores: prompt, sanitized context, top-K retrievals, model/version, timestamp, and a short human-readable rationale.
- Reasoning Explorer exposes chain-of-thought, evidence snippets, and allows reruns with modified prompts.

MVP vertical (prioritized)
1. Corpus ingestion & index (ingest PDFs/notes/OCR + index embeddings).
2. Upload UI + mapping assistant + storage of raw rows.
3. Codex functions: clean_contacts, normalize_address, embed_text, dedupe_group.
4. Enrichment worker: basic public-record enrichment (stubbed provider) and doc_corpus_lookup integration.
5. Scoring pipeline (rules + LLM explainable summary) + opportunities feed UI.
6. Monitor agent (manual start) that synthesizes opportunities from uploads + corpus.
7. Campaign preview (no auto-send) + audit trail.
8. WebSocket progress + Reasoning Explorer basic view.

Metrics & KPIs (lead quality focus)
- Precision@K (top-K opportunities that convert to verified prospects)
- Contact accuracy rate (validated phones/emails)
- Evidence coverage (avg number of supporting documents per opportunity)
- Time-to-verification
- Conversion rate (opportunity → accepted offer)
- Model calibration (confidence vs. actual success)

Cost & scale considerations
- Batch embeddings in off-peak; cache persistent vectors.
- Use smaller embedding models for indexing; use higher-cost LLMs only for on-demand synthesis or negotiation drafts.
- Consider managed vector DB for scale (Pinecone/Weaviate) and Temporal for durable orchestrations at scale.

Security & compliance
- Field-level PII encryption, RBAC, opt-in for skiptrace/outbound.
- Audit logs and retention/deletion tools.
- E-sign and campaign sending gated by explicit permissions.

Next deliverables I can produce (pick one)
- A: Concrete OpenAPI spec + DB migration SQL for uploads + transform_runs + documents + opportunities.
- B: Prioritized GitHub issue backlog (ready to import) implementing the MVP vertical for LetsVenture2021/Tax-Lien-Specialist.
- C: React scaffold for Upload page + Mapping Assistant + WebSocket status panel.

Choose A, B, or C and I will produce the files/issue list/code next.
```

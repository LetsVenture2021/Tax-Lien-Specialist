# 🧠 AI/AGI Layer Extensions – Tax Lien Strategist App

This document defines advanced AI/AGI-layer data structures on top of the existing schema, focused on:

1. **Embedding index structure**
2. **Agent memory schema**
3. **LLM reasoning logs & traceability model**

These extensions are designed to support:
- Long-term semantic memory across properties, liens, counties, and investors
- Rich agent context for planning, error handling, and self-critique
- Full auditability of AGI reasoning for compliance and debugging

Assumptions:
- Base OLTP schema as previously defined
- PostgreSQL with JSONB support and (optionally) the `vector` extension

---
# 1. Embedding Index Structure

## 1.1 Goals
- Provide fast **vector similarity search** over heterogeneous entities (properties, liens, documents, analysis summaries).
- Support both **global indexes** and **type-specific filtering** (e.g., only compare properties-to-properties).

## 1.2 Logical Table: `embeddings`

We previously defined a generic `embeddings` table; here we refine and extend it.

### 1.2.1 Table Definition (PostgreSQL + `pgvector`)

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE ai_embeddings (
    id             BIGSERIAL PRIMARY KEY,
    entity_type    VARCHAR(64) NOT NULL, -- e.g., 'property', 'lien', 'analysis_summary', 'document'
    entity_id      BIGINT NOT NULL,
    embedding      VECTOR(1536) NOT NULL, -- adjust dimension to your model
    model_name     VARCHAR(128) NOT NULL,
    namespace      VARCHAR(64), -- e.g., 'prod', 'test', 'experiment_A'
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (entity_type, entity_id, model_name, namespace)
);

-- HNSW index for similarity search
CREATE INDEX ai_embeddings_embedding_idx
ON ai_embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 200);

-- Optional filtering index
CREATE INDEX ai_embeddings_entity_filter_idx
ON ai_embeddings (entity_type, model_name, namespace);
```

### 1.2.2 Usage Patterns

- **Property semantic lookup:**
  - Given a new property description, embed it and `ORDER BY embedding <-> query_embedding LIMIT k`.
- **Deal context retrieval:**
  - Entity type: `analysis_summary`, store condensed run-level summaries.
  - Retrieve most similar summaries when running a new analysis.
- **Investor behavior:**
  - Entity type: `investor_profile_summary`, to personalize scoring/wording.

---
# 2. Agent Memory Schema

## 2.1 Memory Types

We model memory on three levels:

1. **Episodic Memory** – per agent task & episode
2. **Semantic Memory** – long-lived knowledge (already captured mostly in OLTP + embeddings)
3. **Working Memory** – short-lived context windows during multi-step reasoning

## 2.2 Tables

### 2.2.1 `agent_episodes`
Represents a logical episode of work (could contain multiple tasks).

```sql
CREATE TABLE ai_agent_episodes (
    id               BIGSERIAL PRIMARY KEY,
    episode_uuid     UUID NOT NULL DEFAULT uuid_generate_v4(),
    root_task_id     BIGINT REFERENCES agent_tasks(id) ON DELETE SET NULL,
    agent_type       VARCHAR(32) NOT NULL, -- orchestrator, research, underwriting, document
    started_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at     TIMESTAMPTZ,
    status           VARCHAR(32) NOT NULL DEFAULT 'running',
    summary          TEXT,       -- human-readable summary of episode
    summary_embedding VECTOR(1536),
    metadata         JSONB       -- arbitrary tags, experiment flags, etc.
);

CREATE INDEX ai_agent_episodes_agent_type_idx ON ai_agent_episodes (agent_type, status);
```

### 2.2.2 `agent_memories`
Atomic memory items linked to episodes and/or entities.

```sql
CREATE TABLE ai_agent_memories (
    id                BIGSERIAL PRIMARY KEY,
    episode_id        BIGINT REFERENCES ai_agent_episodes(id) ON DELETE CASCADE,
    memory_type       VARCHAR(32) NOT NULL CHECK (memory_type IN ('episodic','semantic','working')),
    entity_type       VARCHAR(64),    -- e.g., 'property','lien','county','investor','analysis_run'
    entity_id         BIGINT,
    content           TEXT NOT NULL,  -- natural language representation
    embedding         VECTOR(1536),   -- semantic representation
    importance_score  NUMERIC(5,3),   -- priority / recall weight
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ai_agent_memories_episode_idx ON ai_agent_memories (episode_id, memory_type);
CREATE INDEX ai_agent_memories_entity_idx ON ai_agent_memories (entity_type, entity_id);
CREATE INDEX ai_agent_memories_embedding_idx
ON ai_agent_memories
USING hnsw (embedding vector_cosine_ops);
```

**Usage:**
- Store **episodic summaries** after each major decision.
- Promote some memories to `memory_type = 'semantic'` when they represent reusable insights (e.g., "County X has unusually high redemption rates in Q2").

### 2.2.3 `agent_working_sets`
Fast-access working memory snapshots used by agents during planning.

```sql
CREATE TABLE ai_agent_working_sets (
    id              BIGSERIAL PRIMARY KEY,
    episode_id      BIGINT REFERENCES ai_agent_episodes(id) ON DELETE CASCADE,
    agent_task_id   BIGINT REFERENCES agent_tasks(id) ON DELETE CASCADE,
    context_window  JSONB NOT NULL,    -- compact representation of the current prompt context
    token_count     INTEGER,           -- estimated token size of context
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ai_agent_working_sets_episode_task_idx
ON ai_agent_working_sets (episode_id, agent_task_id);
```

**Usage:**
- Log the context (structured metadata, not full prompt) used for each LLM call.
- Later, reconstruct or audit what the model saw at each decision step.

---
# 3. LLM Reasoning Logs & Traceability Model

## 3.1 Goals

- Provide a **full trace** of:
  - What prompts were sent
  - What responses were received
  - What tools were invoked
  - How decisions changed state
- Enable offline **root-cause analysis**, **compliance review**, and **model improvement**.

## 3.2 Tables

### 3.2.1 `llm_calls`
One row per LLM API call.

```sql
CREATE TABLE ai_llm_calls (
    id                 BIGSERIAL PRIMARY KEY,
    agent_task_id      BIGINT REFERENCES agent_tasks(id) ON DELETE SET NULL,
    episode_id         BIGINT REFERENCES ai_agent_episodes(id) ON DELETE SET NULL,
    model_name         VARCHAR(128) NOT NULL,
    prompt             TEXT NOT NULL,        -- redacted or hashed if needed
    prompt_tokens      INTEGER,
    response           TEXT NOT NULL,        -- truncated or redacted in prod if needed
    response_tokens    INTEGER,
    temperature        NUMERIC(3,2),
    top_p              NUMERIC(3,2),
    stop_sequences     TEXT,
    tool_calls         JSONB,                -- structured representation of tools requested
    latency_ms         INTEGER,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ai_llm_calls_task_idx ON ai_llm_calls (agent_task_id);
CREATE INDEX ai_llm_calls_episode_idx ON ai_llm_calls (episode_id);
```

### 3.2.2 `llm_tool_events`
Tracks each tool usage initiated from an LLM call.

```sql
CREATE TABLE ai_llm_tool_events (
    id             BIGSERIAL PRIMARY KEY,
    llm_call_id    BIGINT NOT NULL REFERENCES ai_llm_calls(id) ON DELETE CASCADE,
    tool_name      VARCHAR(128) NOT NULL,
    tool_input     JSONB,
    tool_output    JSONB,
    status         VARCHAR(32) NOT NULL CHECK (status IN ('success','failed')),
    error_message  TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ai_llm_tool_events_call_idx ON ai_llm_tool_events (llm_call_id);
```

### 3.2.3 `llm_decision_events`
Explicit decision/change events driven by LLM reasoning.

```sql
CREATE TABLE ai_llm_decision_events (
    id                BIGSERIAL PRIMARY KEY,
    agent_task_id     BIGINT REFERENCES agent_tasks(id) ON DELETE SET NULL,
    episode_id        BIGINT REFERENCES ai_agent_episodes(id) ON DELETE SET NULL,
    llm_call_id       BIGINT REFERENCES ai_llm_calls(id) ON DELETE SET NULL,
    decision_type     VARCHAR(64) NOT NULL,    -- e.g., 'select_top_deals','skip_county','retry_ingestion'
    decision_payload  JSONB,                   -- structured representation of the decision
    impact_summary    TEXT,                    -- human-readable summary of impact
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ai_llm_decision_events_episode_idx ON ai_llm_decision_events (episode_id, decision_type);
```

---
# 4. Traceability Flows

## 4.1 From Deal to Reasoning

Given a **deal_score** record (for a particular lien and analysis_run):

1. Join to `analysis_runs` to find the run.
2. Join to `agent_tasks` where `analysis_run_id` matches and `agent_type` in (`underwriting`, `orchestrator`).
3. For those tasks, retrieve:
   - `ai_agent_episodes` (episodes)
   - `ai_llm_calls` (all prompts/responses)
   - `ai_llm_decision_events` (what decisions were made)
   - `ai_agent_memories` (what memory chunks were written)
4. (Optional) Use `embedding` similarity search on `ai_agent_memories` to find related past episodes.

## 4.2 From LLM Call to State Change

Given a suspicious or interesting `ai_llm_calls` row:

1. Inspect `tool_calls` → join to `ai_llm_tool_events`.
2. Inspect `decision_events` → join via `llm_call_id`.
3. Trace changes in **OLTP** tables that happened within the same timeframe (e.g., new `deal_metrics`, `risk_assessments`, `documents`).

---
# 5. Example Query Patterns

### 5.1 Find All Episodes That Influenced a Specific Lien

```sql
SELECT DISTINCT e.*
FROM ai_agent_episodes e
JOIN agent_tasks t ON t.id = e.root_task_id OR t.analysis_run_id = ANY (
    SELECT analysis_run_id FROM deal_metrics WHERE lien_id = :lien_id
)
JOIN ai_llm_decision_events d ON d.episode_id = e.id
WHERE d.decision_payload ->> 'lien_id' = CAST(:lien_id AS TEXT);
```

### 5.2 Retrieve Memory Chunks Used Around a Specific Decision

```sql
SELECT m.*
FROM ai_llm_decision_events d
JOIN ai_agent_memories m ON m.episode_id = d.episode_id
WHERE d.id = :decision_event_id
ORDER BY m.importance_score DESC, m.created_at DESC
LIMIT 50;
```

---
# 6. Summary

These AI/AGI layer extensions provide:

- A robust **embedding index** for semantic search across entities and summaries
- A structured **agent memory model** for episodic, semantic, and working memory
- A comprehensive **LLM reasoning log & traceability** framework for:
  - Debugging
  - Compliance and audit
  - Continuous improvement of prompts, tools, and agents

They can be layered on top of the existing OLTP schema with minimal disruption, and selectively enabled in production (e.g., store full prompts in lower environments, hashed or partially redacted in production).

---
**End of AI/AGI Layer Extensions Spec**
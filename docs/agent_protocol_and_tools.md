# Agent Protocol & Tooling Specification – Tax Lien Strategist + AGI / Reasoning Explorer

Version: v1  
Audience: GPT‑5.1 Codex Agent, backend engineers, AI/ML engineers

This document defines the **formal interaction contracts** for all agentic components in the system, including agent responsibilities, input/output schemas, tool signatures, state transitions, logging expectations, and safety constraints.

It ensures deterministic behavior so the Code Agent can implement reliable, auditable agents without ambiguity.

---
# 1. Agent Overview

The application includes four primary agents:

1. **Orchestrator Agent** – coordinates multi-step workflows (analysis runs, task planning, tool delegation).  
2. **Research Agent** – retrieves external data, county liens, valuations, and related info.  
3. **Underwriting Agent** – computes risk, valuations, yields, LTV, and produces decision recommendations.  
4. **Document Agent** – generates investor-facing documents using templates and LLMs.

Agents interact through structured tasks, log events into the Reasoning Explorer tables, and call tools with strict schemas.

---
# 2. Agent Responsibilities

## 2.1 Orchestrator Agent

**Primary role**: Plan and coordinate workflows such as analysis runs, tool calls, research tasks, underwriting tasks, and summarization.

### Responsibilities:
- Validate workflow preconditions.
- Break workflows into tasks.
- Delegate to Research and Underwriting agents.
- Aggregate results.
- Produce final summaries or decisions.
- Log all reasoning steps.

### Required Safety Rules:
- Cannot directly modify DB state (must invoke tools for side-effects).
- Must return structured decisions, not execute them.

### Inputs:
```json
{
  "analysis_run_id": 501,
  "county_id": 5,
  "investor_profile_id": 1,
  "max_budget": 500000,
  "target_yield_min": 0.12
}
```

### Outputs:
```json
{
  "status": "completed",
  "summary": "Identified 80 candidate liens and selected top 50 based on constraints",
  "proposed_decisions": [ ... ]
}
```

---
## 2.2 Research Agent

**Primary role**: Acquire factual data.

### Responsibilities:
- Fetch county lien lists.
- Fetch property details / valuations.
- Retrieve investor or portfolio metadata.
- Clean and normalize external data.

### Required Safety Rules:
- Must not hallucinate missing factual data.
- If data missing → return `null` with explanation.

### Inputs:
```json
{
  "county_id": 5,
  "task": "fetch_liens"
}
```

### Outputs:
```json
{
  "items": [ { "lien_id": 1001, "face_value": 15000, ... } ],
  "missing_fields": []
}
```

---
## 2.3 Underwriting Agent

**Primary role**: Analyze data and compute risk, expected yields, scores.

### Responsibilities:
- Compute LTV (requires property valuation).
- Compute expected yield.
- Produce risk-adjusted scores.
- Generate deal recommendations.

### Required Safety Rules:
- Must follow formulas defined in **Business Rules & Validation Spec**.
- Must not alter persisted data.

### Inputs:
```json
{
  "lien_id": 1001,
  "valuation": 325000,
  "face_value": 15000,
  "days_held": 180
}
```

### Outputs:
```json
{
  "yield": 0.1625,
  "ltv": 0.046,
  "risk_score": 0.2,
  "deal_score": 0.92
}
```

---
## 2.4 Document Agent

**Primary role**: Generate formatted investor‑facing documents.

### Responsibilities:
- Use provided templates.
- Create summaries based on analysis runs.
- Produce documents in PDF/HTML.

### Required Safety Rules:
- Must apply redaction rules.
- Must not output raw PII.

### Inputs:
```json
{
  "template_key": "investment_summary",
  "context": {
    "analysis_run_id": 501,
    "portfolio_id": 10
  }
}
```

### Outputs:
```json
{
  "document_id": 2221,
  "status": "generated",
  "storage_uri": "blob://docs/2221.pdf"
}
```

---
# 3. Task Lifecycle & Episodes

Agents operate in **episodes**, each containing multiple **tasks**.

## 3.1 Task States
- `pending`
- `running`
- `completed`
- `failed`

Each task must log:
- Start time
- End time
- Agent type
- Inputs
- Outputs (summaries)
- Events (LLM calls, tool calls, decisions)

---
# 4. Tool Interface (Function Calling Catalog)

Tools are server-side functions callable by agents. They must be deterministic and validated.

Below are all required tools with schema definitions.

## 4.1 fetch_county_liens
Fetches liens for a county.

### Signature:
```json
{
  "name": "fetch_county_liens",
  "description": "Retrieve all lien records for a given county.",
  "input_schema": {
    "type": "object",
    "properties": {
      "county_id": { "type": "integer" },
      "date_range": {
        "type": "object",
        "properties": {
          "start": { "type": "string", "format": "date-time" },
          "end": { "type": "string", "format": "date-time" }
        }
      }
    },
    "required": ["county_id"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "items": { "type": "array" },
      "total": { "type": "integer" }
    }
  }
}
```

---
## 4.2 fetch_property_details
Fetches property + valuation data.

```json
{
  "name": "fetch_property_details",
  "description": "Retrieve property metadata and valuations.",
  "input_schema": {
    "type": "object",
    "properties": {
      "property_id": { "type": "integer" }
    },
    "required": ["property_id"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "property": { "type": "object" },
      "valuation": { "type": "object", "nullable": true }
    }
  }
}
```

---
## 4.3 compute_lien_metrics
Computes yield, LTV, scores.

```json
{
  "name": "compute_lien_metrics",
  "input_schema": {
    "type": "object",
    "properties": {
      "lien_id": { "type": "integer" }
    },
    "required": ["lien_id"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "yield": { "type": "number" },
      "ltv": { "type": "number" },
      "risk_score": { "type": "number" },
      "deal_score": { "type": "number" }
    }
  }
}
```

---
## 4.4 generate_document_from_template
Generates a document.

```json
{
  "name": "generate_document_from_template",
  "input_schema": {
    "type": "object",
    "properties": {
      "template_key": { "type": "string" },
      "context": { "type": "object" }
    },
    "required": ["template_key", "context"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "document_id": { "type": "integer" },
      "status": { "type": "string" }
    }
  }
}
```

---
## 4.5 update_analysis_run_status
Updates analysis run state.

```json
{
  "name": "update_analysis_run_status",
  "input_schema": {
    "type": "object",
    "properties": {
      "analysis_run_id": { "type": "integer" },
      "status": { "type": "string" },
      "summary": { "type": "string" }
    },
    "required": ["analysis_run_id", "status"]
  }
}
```

---
## 4.6 log_decision_event
Persists a structured decision.

```json
{
  "name": "log_decision_event",
  "input_schema": {
    "type": "object",
    "properties": {
      "episode_id": { "type": "integer" },
      "agent_task_id": { "type": "integer" },
      "decision_type": { "type": "string" },
      "payload": { "type": "object" }
    },
    "required": ["episode_id", "agent


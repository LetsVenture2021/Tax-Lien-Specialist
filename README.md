# Tax Lien Strategist – AGI-Enhanced Investment & Reasoning Platform

## 🚀 Overview
The **Tax Lien Strategist** is a full-stack, agentic, AI-powered investment analysis platform designed to acquire, analyze, and manage tax lien assets with precision. It combines:

- **FastAPI backend** with modular domain services
- **React/TypeScript frontend** with Reasoning Explorer developer tooling
- **LLM-driven AGI agents** (Orchestrator, Research, Underwriting, Document)
- **End-to-end workflow automation** for lien ingestion → analysis → underwriting → portfolio selection
- **Deep observability** into agent reasoning, decisions, and tool calls via the Reasoning Explorer
- **Azure or GCP cloud deployment stacks** for scalable production operation

This README is a high-level operational guide to the system architecture, development environment, and core workflows.

---
## 🧠 Core Capabilities
### 1. Agentic Workflow Automation
- Multi-step workflows executed by the **Orchestrator Agent**
- Domain intelligence powered by **Research** and **Underwriting Agents**
- Document generation through the **Document Agent** with redacted LLM prompts/responses

### 2. Reasoning Explorer (Developer & Compliance Tools)
A complete introspection UI for:
- Agent episodes
- LLM calls (with redaction policies applied)
- Decisions and tool calls
- Memory snapshots & entity context

### 3. Analytical & Data Science Extensions
- Star schema for warehouse analytics
- Materialized views for deal aggregation & yield performance
- Time-series forecasting models for lien pipelines

---
## 🏗️ System Architecture Summary
### Backend
- **FastAPI** application with modular route groups
- Domain layers: Properties, Liens, Investors, Portfolios, Analysis, Agents
- Background jobs: ingestion, valuation refresh, NAV updates, log cleanup
- Postgres + `pgvector` for structured + semantic AI memory
- Redis for queueing, caching, and scheduled jobs

### Frontend
- **React + Vite + TypeScript**
- Feature-oriented folder structure
- Reasoning Explorer UI
- Admin tools for debugging and compliance

### Agents & AGI Layer
- GPT-5.1 (OpenAI)
- HuggingFace models for redaction, classification, and summarization
- Embedded memory vectors and episode tracing

### Deployment Targets
**Azure stack** includes:
- App Service or AKS
- Postgres Flexible Server
- Redis Cache
- Blob Storage

**GCP stack** includes:
- Cloud Run or GKE
- Cloud SQL (Postgres)
- Memorystore
- Cloud Storage

---
## 📁 Repository Structure (High-Level)
```
/infra                 # IaC for Azure or GCP
/backend               # FastAPI source
  /app
    /api
    /core
    /models
    /schemas
    /services
    /ai
    /jobs
/frontend              # React/Vite source
  /src
    /features
    /components
    /config
/docs                  # All specifications + architecture docs
/tests                 # Backend + frontend tests
/scripts               # Seeders, migrations, utilities
```

---
## 🔌 API Specification
Full HTTP API contracts are available in `docs/backend_api_specification.md`. Includes endpoint definitions for:
- Auth
- Investors
- Properties
- Liens
- Analysis Runs
- Portfolios
- Documents
- Agents
- Reasoning Explorer

---
## 📜 Business Rules & Domain Logic
Rules for lien eligibility, redemption windows, investor constraints, deal scoring & LTV/yield computation, and valid status transitions are defined in `docs/business_rules_and_validation_spec.md`.

---
## 🔧 Agents & Tool Protocols
Structured JSON schemas for agent input/output and tool calls live in `docs/agent_protocol_and_tools.md`.

Agents:
- Orchestrator
- Research
- Underwriting
- Document

Tools include:
- `fetch_county_liens`
- `fetch_property_details`
- `compute_lien_metrics`
- `generate_document_from_template`
- `log_decision_event`

---
## 🧩 Background Jobs & Schedules
Defined in `docs/background_jobs_and_scheduling.md`. Covers ingestion, valuation refresh, NAV updates, document generation, reasoning archival, and more.

---
## ⚙️ Local Development
### Requirements
- Python 3.11+
- Node 18+
- Docker / Docker Compose

### Start Full Stack
```
docker compose up --build
```

### Run Backend Tests
```
pytest
```

### Run Frontend
```
cd frontend
npm install
npm run dev
```

---
## 🚀 Deployment
Deployment instructions for Azure and GCP are documented in:
- `docs/azure_stack_and_deployment_plan_tax_lien_strategist.md`
- `docs/gcp_stack_and_deployment_plan_tax_lien_strategist.md`

CI/CD pipelines are defined in `docs/ci_cd_pipeline_specification.md`.

---
## 🧪 Seed Data & Fixtures
Seed data references live in `docs/seed_data_and_test_fixtures.md` and are used for spinning up a fresh dev environment.

---
## 🔍 Observability
Guidelines are in `docs/logging_monitoring_and_slos.md`. Includes structured logging fields, required metrics, SLO definitions, and alert rules.

---
## 🆘 Runbooks & Incident Response
Found in `docs/incident_response_runbooks.md`. Covers LLM outages, DB hotspots, ingestion failures, and worker queues.

---
## 🧭 Vision
The platform serves as a fully agentic, explainable AI system for tax lien investment. It blends operational automation, financial analysis, and AGI-driven reasoning while maintaining transparency, safety, and regulatory compliance.

---
## 📄 License
Proprietary – All rights reserved.

---
## 📬 Contact
For support or questions, contact **Pryceless Ventures LLC**.

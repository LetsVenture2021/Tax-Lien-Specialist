# GCP-Oriented Stack & Deployment Plan – Tax Lien Strategist + AGI / Reasoning Explorer

This document adapts the recommended architecture to **Google Cloud Platform (GCP)** for the Tax Lien Strategist App with an AGI/Agentic layer and Reasoning Explorer.

---
## 1. Core Runtime & App Stack

### Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI (ASGI)
- **Runtime Hosting (recommended path):**
  - Initial: **Cloud Run** (container, fully managed) for API and workers.
  - Scale-up: **Google Kubernetes Engine (GKE)** for full microservices + workers and GPU workloads.

### Frontend
- **React + TypeScript** built with Vite.
- **Hosting options:**
  - **Firebase Hosting** (simple SPA hosting with CDN), or
  - **Cloud Run** (Nginx container serving static files), or
  - **Cloud Storage + Cloud CDN** (static website).

### Background Jobs / Workers
- Containerized worker processes running Celery / RQ / custom workers.
- Deployed as:
  - **Cloud Run Jobs** for scheduled or batch jobs, or
  - Long-running worker service on **Cloud Run** (with concurrency tuned), or
  - Dedicated **GKE Deployment** with autoscaling.

---
## 2. Data & Storage on GCP

### 2.1 Primary Database
- **Cloud SQL for PostgreSQL**
  - Holds OLTP schema (users, properties, liens, portfolios, etc.).
  - Holds AI/AGI tables (`ai_llm_calls`, `ai_agent_episodes`, `ai_agent_memories`, etc.).
  - Enable **pgvector** extension for embeddings.

Recommended configuration:
- Region close to Cloud Run / GKE region (e.g., `us-central1` or `us-east1`).
- Automatic backups and point-in-time recovery (PITR) enabled.
- Separate DB schemas:
  - `public` – OLTP domain tables
  - `dw` – data warehouse/star schema
  - `ai` – AI-oriented tables and vectors (optional but clean).

### 2.2 Object Storage
- **Cloud Storage (GCS)**
  - For documents (contracts, PDFs, AVM reports, generated docs).
  - For analytics exports / snapshots.
  - For model artifacts if you cache HuggingFace models or embeddings.

Typical buckets:
- `tax-lien-docs-original/`
- `tax-lien-docs-generated/`
- `tax-lien-exports/`
- `tax-lien-logs/` (optional if storing raw logs outside Cloud Logging).

### 2.3 Caching & Queues
- **Memorystore (Redis)**
  - Celery backend/broker or general cache.
- **Pub/Sub**
  - For robust messaging (integration events, ingestion pipelines, async processing).

---
## 3. AI / AGI Integration on GCP

You will still use **OpenAI GPT-5.1** and **HuggingFace**, but networking, security, and scaling will be GCP-native.

### 3.1 OpenAI GPT-5.1
- Use the **OpenAI API** directly over HTTPS.
- Store API keys in **Secret Manager**.
- Outbound connectivity:
  - Cloud Run and GKE have outbound internet access by default.
  - Optionally route via **Cloud NAT** if using private GKE nodes.

### 3.2 HuggingFace
Options:
1. **Hosted HF Inference API** – simplest; call via HTTPS.
2. **Containerized models on GKE** – for lower latency / more control.

For (2), typical pattern:
- GKE node pool with **GPU** (e.g., T4 / L4).
- `hf-inference` Deployment exposing a ClusterIP Service.
- FastAPI backend hits `http://hf-inference` via internal DNS.

### 3.3 Vector & Memory
- **pgvector** inside **Cloud SQL for PostgreSQL**.
- Tables:
  - `ai_embeddings` (vector columns like `VECTOR(1536)`).
  - `ai_agent_memories` with embeddings + HNSW/IVFFlat indices.

Alternative (later): deploy a vector DB (e.g., **Qdrant**, **Weaviate**, **Pinecone**) if vector workloads outgrow Postgres. Qdrant/Weaviate can be run on GKE; Pinecone is SaaS.

---
## 4. Analytics & BI on GCP

### 4.1 Warehouse & Reporting

Two-phase approach:

**Phase 1:**
- Use `dw` schema inside Cloud SQL Postgres for star schema and materialized views.

**Phase 2:**
- Migrate or replicate to **BigQuery** as the primary analytics warehouse.
- BI Tool: **Looker Studio** or **Looker**; Power BI/Tableau are also possible.

### 4.2 Data Pipelines
- **Dataflow** or **Cloud Composer (Airflow)** or **Cloud Run jobs** for ETL/ELT.
- Or run **dbt Core**:
  - Either in a Cloud Run job on a schedule, or
  - In CI/CD pipelines (GitHub Actions / Cloud Build).

Use these to:
- Nightly sync OLTP data from Cloud SQL → BigQuery / `dw` schema.
- Refresh materialized views.
- Generate time-series tables for forecasting.

---
## 5. Observability on GCP

### 5.1 Metrics & Logs
- **Cloud Logging** and **Cloud Monitoring (Stackdriver)**
  - Collect logs from FastAPI containers (Cloud Run or GKE) and workers.
  - Metrics for CPU, memory, request latency.
  - Set SLOs and alerts for critical endpoints.

### 5.2 Tracing
- Use **OpenTelemetry** SDK in Python/JS.
- Export traces to **Cloud Trace**.
- Instrument:
  - LLM calls to GPT-5.1 and HF.
  - Long-running analysis and ingestion jobs.
  - Reasoning Explorer API calls (episodes, LLM calls, decisions).

---
## 6. Security, Identity, and Access Control

### 6.1 Identity
- **Identity Platform** or integrate with an external IdP for SSO.
- For internal tools (Reasoning Explorer), consider:
  - **Google Workspace** + OAuth2 for engineers / compliance team.
  - Map Google groups → app roles (`dev`, `compliance`, `analyst`).

### 6.2 Secrets & Key Management
- **Secret Manager**
  - Store OpenAI keys, HuggingFace tokens, DB passwords.
  - Access via service account IAM bindings.

### 6.3 Networking & Access
- **VPC** for Cloud SQL and GKE.
- **Serverless VPC Access** connectors for Cloud Run to reach Cloud SQL on private IP.
- **Private Service Connect** for private access to Cloud SQL.
- **Cloud Armor** + **External HTTP(S) Load Balancer** for WAF and HTTPS termination in front of Cloud Run / GKE.

---
## 7. Deployment Topologies

### 7.1 Phase 1 – Simpler (Cloud Run + Firebase Hosting)

- **Frontend:**
  - Deploy React SPA to **Firebase Hosting** backed by Cloud CDN.

- **Backend API:**
  - Containerize FastAPI and deploy to **Cloud Run** (regionally, e.g., `us-central1`).
  - Configure minimum instances (e.g., 1) and autoscaling limits.

- **Workers:**
  - Option A: **Cloud Run Job** for batch workflows (e.g., nightly analysis runs).
  - Option B: Long-running worker service on Cloud Run (with low concurrency).

Pros:
- Fully managed scaling with minimal ops overhead.
- Simple deployment via `gcloud run deploy` or Cloud Build.

### 7.2 Phase 2 – Scalable & Custom (GKE)

- **GKE cluster** with:
  - `api-deployment` (FastAPI API)
  - `worker-deployment` (Celery / RQ workers)
  - `hf-inference-deployment` (optional HuggingFace models)
  - `qdrant-deployment` (optional vector DB)
- **Ingress** via GKE Ingress + External HTTP(S) Load Balancer.
- Use **Cloud Armor** for WAF and **Managed SSL** certificates for HTTPS.

Pros:
- Fine-grained control over scaling, node pools (including GPUs), sidecars, and networking.
- Easier to co-locate custom AI services (HF, vector DBs) with the main API.

---
## 8. GCP-Specific CI/CD

### 8.1 Pipelines

Two main options:
- **GitHub Actions** deploying to GCP via `gcloud` and `workload identity`.
- **Cloud Build** with Cloud Deploy (GKE) or direct Cloud Run deploys.

Typical stages:
1. Lint + test backend (FastAPI) and frontend (React).
2. Build Docker image(s) and push to **Artifact Registry**.
3. Deploy:
   - Cloud Run: `gcloud run deploy` from CI.
   - GKE: `gcloud container clusters get-credentials` + `kubectl apply` or Helm.
4. Run DB migrations (Alembic) as a separate job.

### 8.2 Environments
- Separate GCP projects or at least distinct configurations for:
  - `dev` – more permissive, cheaper SKUs.
  - `stage` – close to prod for QA.
  - `prod` – hardened, with strict IAM.

Each environment gets:
- Its own Cloud SQL instance (or at least isolated DBs).
- Own Cloud Storage buckets.
- Separate Cloud Run services or GKE namespaces.

---
## 9. Mapping Existing Components to GCP

- **Postgres:** Cloud SQL for PostgreSQL (with pgvector).
- **Object storage:** Cloud Storage (GCS).
- **Queue/cache:** Memorystore (Redis) + Pub/Sub (for messaging).
- **Compute:** Cloud Run (initially) and/or GKE (later).
- **LLM:** OpenAI GPT-5.1 (over HTTPS).
- **HF models:** Hosted HF Inference API or GKE GPU deployments.
- **Secrets:** Secret Manager.
- **Observability:** Cloud Logging + Cloud Monitoring + Cloud Trace.
- **Auth / SSO:** Identity Platform or Google OAuth2.

---
## 10. Next Steps

1. **Provision core GCP resources** in a `dev` project:
   - Cloud SQL for PostgreSQL (with pgvector enabled).
   - Cloud Storage bucket(s) for documents.
   - Memorystore (Redis) and Pub/Sub topic(s) as needed.

2. **Containerize and deploy the backend API**:
   - Build FastAPI Docker image and push to Artifact Registry.
   - Deploy to Cloud Run with proper env vars and Cloud SQL connection.

3. **Deploy the frontend**:
   - Build the React app and deploy to Firebase Hosting or Cloud Storage + Cloud CDN.
   - Point the frontend to the Cloud Run API base URL.

4. **Wire AGI orchestration and AI tables**:
   - Implement `llm_client.py` using GPT-5.1.
   - Implement reasoning logger writing into `ai_llm_calls`, `ai_llm_decision_events`, `ai_agent_episodes`, `ai_agent_memories`.

5. **Deploy Reasoning Explorer**:
   - Implement `/reasoning/v1` endpoints in FastAPI.
   - Build the Reasoning Explorer React feature and ensure it points at those endpoints.

6. **Add observability and SLOs**:
   - Configure Cloud Monitoring dashboards and alerts.
   - Add tracing around LLM calls and long-running workflows.

This plan gives you a clean, GCP-native baseline that still uses GPT-5.1 + HuggingFace in a way that is scalable, observable, and suitable for a regulated, audit-heavy use case like tax lien investing.


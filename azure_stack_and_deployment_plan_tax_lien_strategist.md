# Azure-Oriented Stack & Deployment Plan – Tax Lien Strategist + AGI / Reasoning Explorer

This document adapts the previously recommended stack to **Azure**.

---
## 1. Core Runtime & App Stack

### Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI (ASGI)
- **Runtime Hosting (recommended path):**
  - Initial: **Azure App Service** (Linux, container-based) for API and workers.
  - Scale-up: **Azure Kubernetes Service (AKS)** for full microservices + workers.

### Frontend
- **React + TypeScript** built with Vite.
- **Hosting options:**
  - **Azure Static Web Apps** (ideal for SPA + API integration) or
  - **Azure App Service** (served from Nginx in a container).

### Background Jobs / Workers
- Containerized worker processes running Celery / RQ.
- Deployed as:
  - Separate **App Service** instance or
  - **AKS Deployment** with appropriate scaling.

---
## 2. Data & Storage on Azure

### 2.1 Primary Database
- **Azure Database for PostgreSQL – Flexible Server**
  - Holds OLTP schema (users, properties, liens, portfolios, etc.).
  - Also holds AI/AGI tables (`ai_llm_calls`, `ai_agent_episodes`, `ai_agent_memories`, etc.).
  - Enable **pgvector** extension for embeddings.

Recommended configuration:
- Single region close to AKS/App Service region.
- Automatic backups and PITR enabled.
- Separate DB schemas:
  - `public` – OLTP
  - `dw` – data warehouse/star schema
  - `ai` – AI-oriented tables (optional but clean).

### 2.2 Object Storage
- **Azure Blob Storage**
  - For documents (generated contracts, PDFs, AVM reports).
  - For model artifacts or HF snapshot data (if you cache anything locally).

Typical containers:
- `docs-original/`
- `docs-generated/`
- `exports/`
- `logs/` (if you want raw logs outside App Insights).

### 2.3 Caching & Queues
- **Azure Cache for Redis**
  - Celery backend/broker or general cache.
- **Azure Service Bus** (optional)
  - If you want robust messaging beyond Redis (e.g., integration events between services).

---
## 3. AI / AGI Integration on Azure

You’ll still use **OpenAI GPT‑5.1** and **HuggingFace**, but wiring and security go through Azure services.

### 3.1 OpenAI GPT‑5.1
- Use the **OpenAI API** directly (internet egress) or **Azure OpenAI** if you later migrate models there.
- Store API keys in **Azure Key Vault**.
- Outbound connectivity:
  - If using private AKS/App Service, configure **NAT Gateway** or **Azure Firewall** for egress.

### 3.2 HuggingFace
Options:
1. **Hosted HF Inference API** – easiest; call over HTTPS.
2. **Containerized models in AKS** – use GPU node pools if you need local serving.

For (2), typical pattern:
- AKS node pool with GPU.
- Deployment `hf-inference` exposing an internal ClusterIP service.
- Backend FastAPI calls cluster-internal endpoint.

### 3.3 Vector & Memory
- **pgvector** in Azure PostgreSQL.
- Tables:
  - `ai_embeddings` (with `VECTOR(1536)` columns).
  - `ai_agent_memories` with HNSW or IVFFlat indexes.

Alternative (later): deploy **Qdrant** or **Weaviate** on AKS if vector workloads outgrow Postgres.

---
## 4. Analytics & BI on Azure

### 4.1 Warehouse & Reporting
- Start with `dw` schema inside Azure Postgres.
- Next step: **Azure Synapse Analytics** or **Azure SQL Database** as a dedicated warehouse.
- BI Tool: **Power BI** (natural Azure fit).

### 4.2 Data Pipelines
- **Azure Data Factory** or **Synapse Pipelines** for:
  - Nightly ETL/ELT from OLTP to `dw`.
  - Refreshing materialized views.
- Or run **dbt Core** in CI/CD or scheduled container on AKS/App Service.

---
## 5. Observability on Azure

### 5.1 Metrics & Logs
- **Azure Monitor + Application Insights**
  - Collect logs from FastAPI (structured JSON) and workers.
  - Application maps, request traces, dependencies.

### 5.2 Tracing
- Use **OpenTelemetry** SDK in Python and JS.
- Export traces to Application Insights.
- Particularly important for: LLM calls, long-running analysis jobs, Reasoning Explorer navigation.

---
## 6. Security, Identity, and Access Control

### 6.1 Identity
- **Azure AD (Entra ID)** for SSO:
  - Integrate backend with OAuth2 / OpenID Connect via Azure AD.
  - Map AD groups → app roles (`dev`, `compliance`, `analyst`).

### 6.2 Secrets & Key Management
- **Azure Key Vault**
  - Store OpenAI keys, HuggingFace tokens, DB credentials.
  - Inject into App Service/AKS via managed identity.

### 6.3 Networking
- **Azure Virtual Network (VNet)**
  - Place App Service (Premium), AKS, and Postgres inside or peered with VNet.
- **Private endpoints**
  - For Postgres and Blob Storage.
- **App Gateway / Azure Front Door**
  - For HTTPS termination and WAF in front of frontend + backend.

---
## 7. Deployment Topologies

### 7.1 Phase 1 – Simpler (App Service + Static Web Apps)

- **Frontend:**
  - Deploy React app to **Azure Static Web Apps**.
- **Backend API:**
  - Deploy FastAPI container to **Azure App Service** (Linux, container).
- **Workers:**
  - Separate App Service plan instance running the Celery/RQ worker container.

Pros:
- Simple setup, minimal AKS complexity.
- Azure-managed scaling for API and worker.

### 7.2 Phase 2 – Scalable (AKS)

- **AKS** cluster with:
  - `api-deployment` (FastAPI)
  - `worker-deployment` (Celery workers)
  - `hf-inference-deployment` (optional)
  - `qdrant-deployment` (optional vector DB)
- **Ingress Controller** (NGINX or AGIC) + Application Gateway.
- Still use Azure Static Web Apps or serve frontend via CDN.

Pros:
- Fine-grained control over scaling, node pools, GPU workloads.
- Easier multi-service evolution.

---
## 8. Azure-Specific CI/CD

### 8.1 Pipelines
- Use **GitHub Actions** with Azure integrations:
  - `azure/login` for authentication.
  - `azure/webapps-deploy` for App Service.
  - `azure/aks-set-context` + `kubectl`/`helm` for AKS.

### 8.2 Environments
- **dev**, **stage**, **prod** resource groups.
- Separate:
  - Postgres instances or at least separate DBs.
  - Storage accounts.
  - App Service plans / AKS clusters (depending on criticality).

---
## 9. Mapping Existing Components to Azure

- **Postgres:** Azure Database for PostgreSQL
- **Blob / file storage:** Azure Blob Storage
- **Queue/cache:** Azure Cache for Redis (+ Service Bus if needed)
- **Compute:** App Service and/or AKS
- **LLM:** OpenAI GPT‑5.1 (or Azure OpenAI later)
- **HF models:** Hosted API or AKS GPU deployments
- **Secrets:** Azure Key Vault
- **Observability:** Azure Monitor + Application Insights
- **Auth / SSO:** Azure AD (Entra ID)

---
## 10. Next Steps

1. Stand up **Azure Database for PostgreSQL** (with pgvector enabled).
2. Create a **resource group** for dev and deploy:
   - App Service for API
   - Static Web App for frontend
   - Cache for Redis
   - Key Vault for secrets
3. Wire **FastAPI** to read DB + API keys from Key Vault via managed identity.
4. Deploy the AGI orchestration service and log to `ai_*` tables.
5. Deploy the **Reasoning Explorer** frontend pages against the `/reasoning/v1` endpoints.

This gives you a clean, Azure-native baseline that still uses GPT‑5.1 + HuggingFace in a way that’s scalable, observable, and compliant-friendly.


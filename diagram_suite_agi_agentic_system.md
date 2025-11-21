# Diagram Suite – AGI/Agentic System for Tax Lien Strategist App

This document contains a set of text-based diagrams (Mermaid & UML-style) that can be rendered in compatible tools.

---
## 1. High-Level Architecture (Component + Layers)
```mermaid
flowchart TB
    subgraph UI[User & UI Layer]
        Investor[Investor / User]
        WebUI[Web UI (Next.js/React)]
    end

    subgraph API[API Gateway / BFF]
        APIGW[API Gateway (FastAPI/Node)]
    end

    subgraph CORE[Core Analysis Layer]
        DealEng[Deal Analysis Engine]
        RiskEng[Risk Intelligence Engine]
        PortMgr[Portfolio Manager]
    end

    subgraph AGI[Agentic Intelligence Layer]
        Orchestrator[Orchestrator Agent]
        ResearchA[Autonomous Research Agent]
        UnderwriterA[Underwriting Agent]
        DocA[Document Agent]
    end

    subgraph DATA[Data Persistence Layer]
        DB[(PostgreSQL)]
        VecDB[(Vector DB)]
        Cache[(Redis)]
        ObjStore[(Object Storage)]
    end

    subgraph EXT[External Systems]
        County[County / Tax Data]
        MLS[MLS / Zillow / ATTOM]
        Maps[GIS / Maps]
        AGIAPI[AGI / LLM Provider]
        Notif[Email / SMS / In-App]
    end

    Investor --> WebUI --> APIGW

    APIGW --> DealEng
    APIGW --> RiskEng
    APIGW --> PortMgr
    APIGW --> Orchestrator

    Orchestrator --> ResearchA
    Orchestrator --> UnderwriterA
    Orchestrator --> DocA

    ResearchA --> County
    ResearchA --> MLS
    ResearchA --> Maps

    Orchestrator --> AGIAPI
    ResearchA --> AGIAPI
    UnderwriterA --> AGIAPI
    DocA --> AGIAPI

    DealEng --> DB
    RiskEng --> DB
    PortMgr --> DB
    Orchestrator --> DB
    ResearchA --> DB

    Orchestrator --> VecDB
    ResearchA --> VecDB
    UnderwriterA --> VecDB
    DocA --> VecDB

    CORE --> Cache
    AGI --> Cache

    DocA --> ObjStore

    PortMgr --> Notif
    DocA --> Notif
```

---
## 2. Detailed Component Diagram (UML-Style Text)

```text
+---------------------------------------------------------+
|                 Tax Lien Strategist System              |
+---------------------------------------------------------+
| Components:                                             |
|  - WebUI (Next.js/React)                               |
|  - API Gateway (FastAPI/Node)                          |
|  - DealAnalysisService                                 |
|  - RiskEngineService                                   |
|  - PortfolioService                                    |
|  - AgentOrchestrator                                   |
|  - ResearchAgent                                       |
|  - UnderwritingAgent                                   |
|  - DocumentAgent                                       |
|  - Persistence Layer (PostgreSQL, Redis, S3, VectorDB) |
+---------------------------------------------------------+

[WebUI] --HTTP/JSON--> [API Gateway]
[API Gateway] --gRPC/REST--> [DealAnalysisService]
[API Gateway] --gRPC/REST--> [RiskEngineService]
[API Gateway] --gRPC/REST--> [PortfolioService]
[API Gateway] --gRPC/REST--> [AgentOrchestrator]

[AgentOrchestrator] --Tasks--> [ResearchAgent]
[AgentOrchestrator] --Tasks--> [UnderwritingAgent]
[AgentOrchestrator] --Tasks--> [DocumentAgent]

[ResearchAgent] --HTTP--> [County/APIs]
[ResearchAgent] --HTTP--> [MLS/ATTOM]
[ResearchAgent] --HTTP--> [GIS/Maps]

[All Agents] --LLM Calls--> [AGI Provider]

[DealAnalysisService] --SQL--> [PostgreSQL]
[RiskEngineService] --SQL--> [PostgreSQL]
[PortfolioService] --SQL--> [PostgreSQL]
[Agents] --SQL--> [PostgreSQL]

[Agents] --Vector Ops--> [VectorDB]
[Core Services] --Cache--> [Redis]
[DocumentAgent] --PUT/GET--> [Object Storage]
```

---
## 3. Sequence Diagram – "Analyze New County Auction"

```mermaid
sequenceDiagram
    participant User as Investor
    participant UI as Web UI
    participant API as API Gateway
    participant OA as Orchestrator Agent
    participant RA as Research Agent
    participant UA as Underwriting Agent
    participant DA as Document Agent
    participant DE as Deal Engine
    participant DB as PostgreSQL
    participant LLM as AGI Provider

    User->>UI: Request("Analyze County X Auction")
    UI->>API: POST /analyze/countyX
    API->>OA: createTask(county="X")

    OA->>LLM: Plan(decompose request)
    LLM-->>OA: Plan: [fetch_lists, enrich, underwrite, summarize]

    OA->>RA: task(fetch_lists+enrich)
    RA->>County: GET auction lists
    County-->>RA: raw CSV/HTML/PDF
    RA->>LLM: extract + normalize(raw data)
    LLM-->>RA: structured lien/property records
    RA->>DB: INSERT properties, liens

    OA->>UA: task(underwrite county X)
    UA->>DB: SELECT normalized lien/property
    UA->>LLM: reasoning + scenario modeling
    LLM-->>UA: scenario EVs, risk notes
    UA->>DE: send metrics for deterministic calc
    DE->>DB: write deal metrics & scores

    OA->>DA: task(generate summary docs)
    DA->>DB: SELECT top deals for county X
    DA->>LLM: generate investor summary
    LLM-->>DA: natural language report
    DA->>ObjStore: store PDF/HTML report

    API->>DB: fetch top deals + report link
    API-->>UI: JSON (deals + report_url)
    UI-->>User: Display results & download link
```

---
## 4. Sequence Diagram – "Investor Requests Top 10 Deals"

```mermaid
sequenceDiagram
    participant User as Investor
    participant UI as Web UI
    participant API as API Gateway
    participant DE as Deal Analysis Service
    participant OA as Orchestrator Agent
    participant DB as PostgreSQL

    User->>UI: Request("Top 10 deals") with filters
    UI->>API: GET /deals/top10?filters
    API->>DE: getTopDeals(filters)

    alt Cached/Precomputed
        DE->>DB: SELECT from deal_scores WHERE filters
        DB-->>DE: deal_rows
    else Missing / Stale
        DE->>OA: requestRecompute(filters)
        OA->>DE: asyncTaskAck
        note right of OA: Orchestrator may spawn
        note right of OA: Research/Underwriting Agents
        OA->>DB: write new metrics & scores
        DE->>DB: SELECT updated deal_scores
        DB-->>DE: deal_rows
    end

    DE-->>API: deals[10]
    API-->>UI: JSON deals[10]
    UI-->>User: Render top 10 deals grid
```

---
## 5. Deployment Diagram

```text
+-----------------------------+          +-----------------------------+
|        User Environment     |          |       Cloud Environment     |
+-----------------------------+          +-----------------------------+
|  Browser / Client           |          |  Region: us-central-1       |
|  - React/Next.js UI         |          |                             |
+--------------+--------------+          +---------------+-------------+
               | HTTP(S)                                 |
               v                                         v
       +-------+-----------------------------+   +-------+--------------------+
       |        API / Edge Layer             |   |  External Services        |
       |  - API Gateway / Load Balancer      |   |  - County APIs            |
       |  - Auth / Rate Limiting             |   |  - MLS/ATTOM/Zillow       |
       +----------------------+--------------+   |  - Maps / GIS             |
                              |                  |  - AGI / LLM Provider     |
                              v                  +---------------------------+
         +--------------------+---------------------------------------------+
         |                 Application Cluster                              |
         |  - Web/API Pods (FastAPI/Node)                                   |
         |  - Core Services Pods (Deal, Risk, Portfolio)                    |
         |  - Agentic Pods (Orchestrator, Research, Underwriting, Document) |
         +--------------------+--------------------+------------------------+
                              |                    |
                              |                    |
            +-----------------+----+         +-----+----------------------+
            | Data Cluster          |         | Eventing & Cache Layer    |
            | - PostgreSQL (RDS)    |         | - Redis                   |
            | - Vector DB           |         | - Message Broker (Kafka)  |
            | - Object Storage (S3) |         +---------------------------+
            +-----------------------+
```

---
## 6. Deployment Diagram (Mermaid Version)
```mermaid
flowchart TB
    subgraph Client[Client]
        Browser[Browser / React UI]
    end

    subgraph Cloud[Cloud Infrastructure]
        subgraph Edge[Edge & API Layer]
            LB[Load Balancer]
            APIServer[API Gateway]
        end

        subgraph AppCluster[Application Cluster]
            WebPods[Web/API Pods]
            CorePods[Core Analysis Pods]
            AgentPods[Agentic Pods]
        end

        subgraph DataCluster[Data & Storage]
            PG[(PostgreSQL)]
            VDB[(Vector DB)]
            RDS[(Redis / Cache)]
            S3[(Object Storage)]
        end

        subgraph Ext[External Services]
            CountyAPI[County APIs]
            MLSAPI[MLS / Zillow]
            MapsAPI[Maps / GIS]
            LLMAPI[AGI / LLM Provider]
        end
    end

    Browser --> LB --> APIServer
    APIServer --> WebPods
    APIServer --> CorePods
    APIServer --> AgentPods

    CorePods --> PG
    CorePods --> RDS
    AgentPods --> PG
    AgentPods --> VDB
    AgentPods --> S3

    AgentPods --> CountyAPI
    AgentPods --> MLSAPI
    AgentPods --> MapsAPI
    AgentPods --> LLMAPI
```

---
## 7. How to Use These Diagrams
- **Mermaid blocks** can be pasted directly into Mermaid-compatible editors (e.g., Markdown previewers, VSCode extensions, Mermaid Live Editor).
- **UML-style text diagrams** can be imported or translated into tools such as PlantUML, Lucidchart, or Draw.io.
- The diagrams are designed to be consistent with the previously defined system architecture, DFDs, and whitepaper.

---
**End of Diagram Suite**


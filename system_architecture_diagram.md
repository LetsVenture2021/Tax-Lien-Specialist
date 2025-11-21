# Tax Lien Strategist App – System Architecture Diagram

Below is a structured, text-based architectural diagram representing major system components, data flow, and agentic layers in the Tax Lien Strategist App.

```
                         ┌──────────────────────────┐
                         │      FRONTEND (UI)       │
                         │ ──────────────────────── │
                         │  Next.js / React / TS    │
                         │  TailwindCSS             │
                         │  Agentic UI Layer        │
                         │  User Dashboard          │
                         └─────────────┬────────────┘
                                       │
                                       ▼
                 ┌────────────────────────────────────────┐
                 │           API GATEWAY / BFF            │
                 │      (FastAPI or Node.js Layer)        │
                 └─────────────┬──────────────────────────┘
                               │
                               ▼
        ┌───────────────────────────────────────────────────────────────┐
        │                         BACKEND CORE                          │
        │ ───────────────────────────────────────────────────────────── │
        │                                                               │
        │  ┌───────────────────────┐    ┌────────────────────────────┐ │
        │  │  Deal Analysis Engine │    │   Risk Intelligence Engine │ │
        │  │ - Comps / ARV         │    │ - Title complexity          │ │
        │  │ - Yield calc          │    │ - Vacancy risk              │ │
        │  │ - ROI, IRR            │    │ - Neighborhood scoring      │ │
        │  └───────────────────────┘    └────────────────────────────┘ │
        │                                                               │
        │  ┌───────────────────────┐    ┌────────────────────────────┐ │
        │  │ Portfolio Manager     │    │  Automation & Alerts Layer │ │
        │  │ - Track liens/deeds   │    │ - Redemption alerts         │ │
        │  │ - Redemption status    │    │ - Foreclosure windows       │ │
        │  │ - Reporting           │    │ - Investor notifications     │ │
        │  └───────────────────────┘    └────────────────────────────┘ │
        │                                                               │
        └───────────────────────┬───────────────────────────────────────┘
                                │
                                ▼
       ┌────────────────────────────────────────────────────────────────┐
       │                    AGI / AGENTIC LAYER                         │
       │ ────────────────────────────────────────────────────────────── │
       │                                                               │
       │  ┌──────────────────────────┐   ┌───────────────────────────┐ │
       │  │ Autonomous Research Agent│   │ Agent Coordinator / Orchestrator│ │
       │  │ - County scraping        │   │ - Multi-agent scheduling   │ │
       │  │ - GIS extraction         │   │ - Policy & task routing    │ │
       │  │ - Auction list ingest    │   │ - Memory mgmt              │ │
       │  └──────────────────────────┘   └───────────────────────────┘ │
       │                                                               │
       │  ┌──────────────────────────┐   ┌───────────────────────────┐ │
       │  │ Deal Underwriting Agent │   │ Document Generation Agent │ │
       │  │ - Valuation             │   │ - Promissory notes         │ │
       │  │ - Scenario modeling     │   │ - Investor packets         │ │
       │  │ - Deed pathway          │   │ - Foreclosure docs         │ │
       │  └──────────────────────────┘   └───────────────────────────┘ │
       │                                                               │
       └──────────────────────┬────────────────────────────────────────┘
                               │
                               ▼
               ┌─────────────────────────────────────────────┐
               │                 DATA LAYER                  │
               │ ─────────────────────────────────────────── │
               │                                             │
               │  PostgreSQL (Structured Data)               │
               │  Redis (Caching, Task Queues)               │
               │  S3 Storage (Docs / Exports)                │
               │  Vector DB (Agent Memory + Embeddings)      │
               │                                             │
               └──────────────────────────────────────────────┘
                               │
                               ▼
                 ┌───────────────────────────────────────────┐
                 │        External Integrations Layer        │
                 │ ───────────────────────────────────────── │
                 │                                           │
                 │ County APIs / GIS Systems                 │
                 │ Zillow / MLS / Redfin / ATTOM             │
                 │ Auction Platforms                         │
                 │ Google Maps / Geocoding                   │
                 │ Satellite & Street Image Models           │
                 │                                           │
                 └───────────────────────────────────────────┘
```


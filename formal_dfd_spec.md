# Formal Data Flow Diagram (DFD) Specification
## Tax Lien Strategist App

This document provides the formal, structured Data Flow Diagram (DFD) specification for the Tax Lien Strategist App, incorporating AGI and agentic architecture components.

---
# **DFD Level 0 – Context Diagram Specification**

### **Process 0: Tax Lien Strategist System**
The entire platform is treated as a single black‑box system.

### **External Entities:**
1. **EE1 – Investor/User**
2. **EE2 – County & Tax Data Sources** (Auction lists, assessor, GIS, clerk)
3. **EE3 – Property Data Providers** (Zillow/MLS/ATTOM)
4. **EE4 – Notification Channels** (Email, SMS, In-app)
5. **EE5 – AGI/LLM Provider**

### **Data Flows:**
- **DF1:** User criteria, commands, and filters → Process 0
- **DF2:** Deal results, dashboards, documents → Investor/User
- **DF3:** Data requests to counties → County Data Sources
- **DF4:** Raw lien/property data → System
- **DF5:** Comps/valuation queries → Property Data Provider
- **DF6:** Comps/market data → System
- **DF7:** LLM tasks, embeddings → AGI Provider
- **DF8:** Reasoning results, generated content → System
- **DF9:** Alerts, reminders, reports → Notification Channels

---
# **DFD Level 1 – Decomposition of Core System**

The Tax Lien Strategist System splits into five major processes:
- **P1: User Interface & API Gateway**
- **P2: Core Analysis Engine**
- **P3: Agentic Intelligence Layer**
- **P4: Data Persistence Layer**
- **P5: Notification & Automation System**

---
## **Process P1 – User Interface & API Gateway**
**Description:** Handles requests from the UI, validates input, and routes tasks to internal services or agentic workflows.

### Data Stores:
- None directly.

### Data Flows:
- **DF1.1:** Investor commands → P1
- **DF1.2:** P1 routes structured requests → P2
- **DF1.3:** P1 routes agentic tasks → P3
- **DF1.4:** P1 sends output data (deals, dashboards, docs) → Investor
- **DF1.5:** P1 queries → P4
- **DF1.6:** Data (property, risk, portfolio) from P4 → P1 → user

---
## **Process P2 – Core Analysis Engine**
**Description:** Performs deal analysis, risk scoring, ROI modeling, redemption probabilities, and foreclosure projections.

### Subprocesses:
- **P2.1 – Deal Analysis Engine**
- **P2.2 – Risk Intelligence Engine**
- **P2.3 – Portfolio Manager**

### Data Stores:
- Writes to **DS1 – PostgreSQL Database**
- Reads from **DS1**

### Data Flows:
- **DF2.1:** Input criteria from P1 → P2.1
- **DF2.2:** Property data from P3 or DS1 → P2.1
- **DF2.3:** Risk indicators from P3 or DS1 → P2.2
- **DF2.4:** ROI, IRR, yield outputs → P1
- **DF2.5:** Portfolio results → P1
- **DF2.6:** Analysis outputs → DS1

---
## **Process P3 – Agentic Intelligence Layer**
**Description:** Houses all AGI-driven autonomous agents and the Agent Orchestrator.

### Subprocesses:
- **P3.1 – Agent Orchestrator**
- **P3.2 – Autonomous Research Agent**
- **P3.3 – Underwriting Agent**
- **P3.4 – Document Generation Agent**

### Data Stores:
- Reads/writes **DS1 – PostgreSQL**
- Reads/writes **DS2 – Vector Database**
- Reads/writes **DS3 – Object Storage** (documents)
- Uses **DS4 – Redis Cache/Queue**

### Data Flows:
- **DF3.1:** Tasks from P1 → P3.1
- **DF3.2:** P3.1 issues subtasks → P3.2/P3.3/P3.4
- **DF3.3:** County data requests → EE2
- **DF3.4:** Raw county data → P3.2
- **DF3.5:** Property data queries → EE3
- **DF3.6:** Market data → P3.2 → P3.3
- **DF3.7:** LLM reasoning requests → EE5
- **DF3.8:** Generated responses → Agents
- **DF3.9:** Extracted/cleaned data → P2
- **DF3.10:** Embeddings → DS2
- **DF3.11:** Generated docs → DS3

---
## **Process P4 – Data Persistence Layer**
**Description:** Provides durable storage for structured, cached, vectorized, and file-based data.

### Data Stores:
- **DS1 – PostgreSQL (Structured Data)**
- **DS2 – Vector DB (Embeddings/Memory)**
- **DS3 – Object Storage (Docs)**
- **DS4 – Redis (Cache & Queues)**

### Data Flows:
- **DF4.1:** Read/write operations ↔ P2
- **DF4.2:** Read/write operations ↔ P3
- **DF4.3:** Cache operations ↔ P2/P3
- **DF4.4:** Document retrieval ↔ P1

---
## **Process P5 – Notification & Automation System**
**Description:** Handles alerts, redemption reminders, foreclosure deadlines, and investor reporting.

### Subprocesses:
- **P5.1 – Automation Engine** (scan DB for triggers)
- **P5.2 – Notification Service**

### Data Stores:
- Reads from **DS1 – PostgreSQL**

### Data Flows:
- **DF5.1:** Trigger events from DB → P5.1
- **DF5.2:** Alert payloads → P5.2
- **DF5.3:** Alerts, emails, SMS → EE4
- **DF5.4:** Logs → DS1

---
# **DFD Level 2 – Decomposition of Agentic Layer (P3)**

## **Process P3.1 – Agent Orchestrator**
- Receives tasks from UI/API.
- Routes tasks to appropriate agents.
- Manages task dependencies, memory, and retries.
- Communicates with AGI for planning and reasoning.

### Data Flows:
- **DF3.1.1:** Task request → Orchestrator
- **DF3.1.2:** Subtask routing → P3.2/P3.3/P3.4
- **DF3.1.3:** Memory operations → DS2
- **DF3.1.4:** LLM planning → EE5

---
## **Process P3.2 – Autonomous Research Agent**
- Collects and normalizes county, GIS, and auction data.
- Queries property data providers.

### Data Flows:
- **DF3.2.1:** County request → EE2
- **DF3.2.2:** Raw data → P3.2
- **DF3.2.3:** Clean data → DS1
- **DF3.2.4:** Structured data → P2

---
## **Process P3.3 – Underwriting Agent**
- Applies valuation models and AGI reasoning.
- Creates risk and ROI projections.

### Data Flows:
- **DF3.3.1:** Property data from P3.2 → P3.3
- **DF3.3.2:** Comps from EE3 → P3.3
- **DF3.3.3:** Underwriting outputs → P2

---
## **Process P3.4 – Document Generation Agent**
- Produces investor reports, promissory notes, foreclosure packets.

### Data Flows:
- **DF3.4.1:** Doc tasks from Orchestrator → P3.4
- **DF3.4.2:** Generated docs → DS3
- **DF3.4.3:** Doc links → P1
- **DF3.4.4:** Email-ready docs → P5.2

---
# **Data Store Definitions**

### **DS1 – PostgreSQL:**
Holds normalized property data, lien information, user profiles, portfolio data, analysis results, and logs.

### **DS2 – Vector Database:**
Stores embeddings, memory objects, conversation context, property semantic representations.

### **DS3 – Object Storage:**
Stores all documents, exports, PDF reports, legal packets.

### **DS4 – Redis:**
Used for caching, task queues, rate-limiting, and ephemeral agent state.

---
# **Compliance & Data Constraints**
- All county-sourced data must be traceable (timestamp, county, source URL).
- All investor data must comply with security and privacy requirements.
- All AGI-generated documents must be archived with metadata.
- Redemption/foreclosure deadlines must be validated to avoid missed events.

---
# **End of DFD Specification**


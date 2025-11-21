# Level 3 Deep-Dive – Deal Analysis Engine (P2.1)
## Tax Lien Strategist App – Detailed DFD Decomposition

This document provides a Level 3 decomposition of **P2.1 – Deal Analysis Engine**, one of the core subsystems responsible for evaluating tax lien and tax deed opportunities.

---
# 1. Overview of P2.1 – Deal Analysis Engine

**Objective:**
Transform raw property, lien, and market data into actionable investment metrics such as **yield**, **ROI**, **IRR**, **LTV**, and **scenario outcomes** (redeem vs. foreclose vs. assign).

**Primary Inputs:**
- User investment criteria (budget, target yield, geography, risk tolerance)
- Property & lien data (from Research Agent and DB)
- Market & comps data (from Underwriting Agent / external APIs)

**Primary Outputs:**
- Scored deals with key metrics
- Ranked deal lists by investor-specific criteria
- Analysis artifacts for downstream agents and UI

---
# 2. Level 3 Processes for P2.1

P2.1 is decomposed into the following subprocesses:

- **P2.1.1 – Input Normalization & Validation**
- **P2.1.2 – Financial Metric Computation**
- **P2.1.3 – Scenario Analysis & Pathway Modeling**
- **P2.1.4 – Deal Scoring & Ranking**
- **P2.1.5 – Persistence & Exposure to UI/Agents**

---
## 2.1 Process P2.1.1 – Input Normalization & Validation

**Description:**
Ensures all incoming data is structured, typed, and within valid ranges before financial computation.

**Inputs:**
- Investment criteria from **P1 – UI/API** (DF2.1.1)
- Property & lien records from **DS1 – PostgreSQL** and **P3.2 – Research Agent** (DF2.1.2)
- Market and comps from **P3.3 – Underwriting Agent** (DF2.1.3)

**Outputs:**
- Normalized property-lien-comps dataset (DF2.1.4) → P2.1.2
- Error & anomaly logs (DF2.1.5) → DS1

**Key Validation Rules:**
- Required fields: parcel ID, county, lien amount, interest rate, redemption period.
- Numeric sanity checks (non-negative values, max thresholds, date coherency).
- Currency and unit normalization (e.g., months vs. days for redemption period).

---
## 2.2 Process P2.1.2 – Financial Metric Computation

**Description:**
Derives baseline financial metrics for each candidate deal.

**Inputs:**
- Normalized dataset from P2.1.1 (DF2.1.4)

**Core Computations:**
- **Lien Yield (Simple / Annualized)**
- **Effective Interest Rate** given local statutory rules
- **Estimated Redemption Amount**
- **Estimated Holding Time** (based on historical/redemption probabilities)
- **Cash-on-Cash Return (COCR)**
- **Loan-to-Value (LTV)** using AVM or comps
- **Projected Foreclosure Cost** (if deed path pursued)

**Outputs:**
- Per-deal financial metrics (DF2.1.6) → P2.1.3
- Aggregated metrics for portfolios (optional) → P2.1.5

**Data Stores Accessed:**
- **DS1 – PostgreSQL:** regulatory tables, historical redemption stats

---
## 2.3 Process P2.1.3 – Scenario Analysis & Pathway Modeling

**Description:**
Models multiple potential paths for each lien/deed:
- Redemption occurs
- Redemption fails → foreclosure
- Assignment/sale of lien before redemption deadline

**Inputs:**
- Financial metrics from P2.1.2 (DF2.1.6)
- Risk scores from **P2.2 – Risk Engine** (DF2.2.x)
- Investor strategy parameters from UI (e.g., prefers quick redemption vs. asset conversion) (DF2.1.7)

**Scenario Types:**
1. **Redemption Scenario:**
   - Expected return = interest + penalties over expected holding period.
2. **Deed Conversion Scenario:**
   - Incorporates ARV, rehab costs, resale discounts.
3. **Assignment / Flip of Lien:**
   - Margin based on discount to face value vs. resell price.

**Outputs:**
- Scenario matrix per deal: [Redemption, Deed, Assignment] (DF2.1.8)
- Expected value (EV) per scenario and global EV per deal (DF2.1.9)

---
## 2.4 Process P2.1.4 – Deal Scoring & Ranking

**Description:**
Transforms scenario outcomes and risk metrics into composite scores tailored to the investor.

**Inputs:**
- Scenario matrix and EV per deal → P2.1.4
- Risk scores from **P2.2 – Risk Engine**
- Investor preferences (e.g., weight on yield vs. safety vs. liquidity)

**Scoring Dimensions:**
- Yield Score
- Risk-Adjusted Return Score
- Liquidity Score
- Volatility / Uncertainty Score
- Strategy Fit Score (alignment with investor’s profile)

**Scoring Logic:**
- Weighted multi-factor model
- Optionally enhanced by AGI (via P3.3) to adjust weights based on historical performance.

**Outputs:**
- Ranked deal list per investor profile (DF2.1.10) → P2.1.5
- Score breakdown per deal (for transparency) → P1 UI

---
## 2.5 Process P2.1.5 – Persistence & Exposure to UI/Agents

**Description:**
Responsible for writing outputs to storage and making results available to UI and agents.

**Inputs:**
- Ranked deal list and score breakdown → P2.1.5

**Actions:**
- Write deal evaluations, scores, and scenarios to **DS1 – PostgreSQL** (DF2.1.11)
- Publish events to **DS4 – Redis** (e.g., 
  - “New Deal Batch Evaluated”
  - “Top Deals Updated for Investor X”)
- Provide API-ready payloads to **P1 – UI/API** (DF2.1.12)
- Provide structured outputs to **P3.1 – Agent Orchestrator** for:
  - Automated buying suggestions
  - Document generation (investment summaries)

**Outputs:**
- Deal evaluation API responses to UI
- Signals for Agentic layer (e.g., tasks for Document Agent or Automation Engine)

---
# 3. Detailed Data Flow List (Level 3 – Deal Analysis Engine)

- **DF2.1.1:** Investment criteria → P2.1.1
- **DF2.1.2:** Property & lien data → P2.1.1
- **DF2.1.3:** Comps/market data → P2.1.1
- **DF2.1.4:** Normalized dataset → P2.1.2
- **DF2.1.5:** Validation errors/logs → DS1
- **DF2.1.6:** Financial metrics → P2.1.3
- **DF2.1.7:** Strategy parameters → P2.1.3
- **DF2.1.8:** Scenario outputs → P2.1.4
- **DF2.1.9:** EV metrics → P2.1.4
- **DF2.1.10:** Ranked deal list → P2.1.5
- **DF2.1.11:** Persisted analysis results → DS1
- **DF2.1.12:** Deal data for UI and agents → P1, P3

---
# 4. Non-Functional Considerations for Deal Analysis Engine

- **Performance:**
  - Must handle batch evaluation of thousands of liens per county in minutes.
  - Utilize vectorized operations and background workers.

- **Accuracy & Auditability:**
  - All metric formulas must be deterministic and versioned.
  - Maintain an audit log per evaluated deal (inputs + outputs).

- **Explainability:**
  - Provide a human-readable breakdown of how scores were derived.
  - Integrate with AGI layer to generate natural language explanations.

- **Extensibility:**
  - Plug-in architecture for new metric types (e.g., tax benefits, JV splits).
  - Configurable scoring models per investor or per fund.

---
# 5. Summary

This Level 3 DFD deep-dive defines the internal mechanics of the **Deal Analysis Engine (P2.1)** as a structured pipeline: normalize → compute → model scenarios → score → persist & expose. It ensures that the metrics feeding the UI, agents, and automation are reliable, explainable, and adaptable to different investment strategies.

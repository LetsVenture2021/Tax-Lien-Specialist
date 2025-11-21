# 📊 Analytical Extensions – Tax Lien Strategist App

This document defines analytical extensions on top of the OLTP data model, including:

1. Data warehouse **star-schema** design
2. **Materialized views** for analytics
3. **Time-series models** for forecasting

Assumptions:
- Source system: PostgreSQL OLTP (as previously defined)
- Analytics environment: PostgreSQL (same instance or separate DW schema) or cloud warehouse (e.g., Snowflake/BigQuery/Redshift) with minor syntax adjustments.

---
# 1. Data Warehouse Star-Schema

## 1.1 Core Analytical Grain

**Fact grain:** one row per **lien per analysis run** with associated metrics and scores.

### Fact Table: `fact_lien_analysis`

**Grain:** (analysis_run_id, lien_id)

Columns (example):
- `fact_id` (PK, surrogate)
- `analysis_run_id` (FK → dim_analysis_run)
- `lien_id` (FK → dim_lien)
- `property_id` (FK → dim_property)
- `county_id` (FK → dim_county)
- `investor_profile_id` (FK → dim_investor)
- `portfolio_id` (nullable FK → dim_portfolio)
- `analysis_date_key` (FK → dim_date)

**Measures (from deal_metrics, risk_assessments, scenario_analyses, deal_scores):**
- `lien_principal_amount`
- `avm_value`
- `lien_to_value_ratio`
- `estimated_redemption_hold_months`
- `simple_yield`
- `annualized_yield`
- `cash_on_cash_return`
- `irr_redemption_scenario`
- `irr_deed_scenario`
- `expected_value_overall`
- `title_risk_score`
- `structural_risk_score`
- `neighborhood_risk_score`
- `vacancy_risk_score`
- `overall_risk_score`
- `prob_redemption`
- `prob_deed_conversion`
- `prob_assignment`
- `proj_profit_redemption`
- `proj_profit_deed`
- `proj_profit_assignment`
- `composite_score`
- `yield_score`
- `risk_adjusted_return_score`
- `liquidity_score`
- `strategy_fit_score`

Optional portfolio performance measures (using portfolio_holdings):
- `realized_profit`
- `realized_roi`
- `is_owned` (0/1)
- `is_redeemed` (0/1)
- `is_foreclosed` (0/1)

---
## 1.2 Dimension Tables

### `dim_date`
Standard date dimension.
- `date_key` (PK, INT, e.g., 20251121)
- `date` (DATE)
- `year`
- `quarter`
- `month`
- `day`
- `weekday`
- `is_weekend`

### `dim_county`
- `county_id` (PK)
- `state_code`
- `county_name`
- `auction_type`
- `timezone`

### `dim_property`
- `property_id` (PK)
- `county_id` (FK → dim_county)
- `apn`
- `street_address`
- `city`
- `state`
- `zip_code`
- `property_type`
- `land_sqft`
- `building_sqft`
- `year_built`
- `zoning`
- `geohash` / lat-lng bucket (optional for spatial rollups)

### `dim_lien`
- `lien_id` (PK)
- `property_id`
- `county_id`
- `lien_certificate_number`
- `lien_type`
- `interest_rate_nominal`
- `interest_type`
- `redemption_period_months`
- `issue_date`
- `redemption_deadline`

### `dim_investor`
- `investor_profile_id` (PK)
- `user_id`
- `display_name`
- `strategy_type`
- `min_target_yield`
- `max_risk_score`
- `time_horizon_months`

### `dim_portfolio`
- `portfolio_id` (PK)
- `investor_profile_id`
- `name`
- `description`

### `dim_analysis_run`
- `analysis_run_id` (PK)
- `analysis_type`
- `analysis_date_key` (FK → dim_date)
- `target_county_id`
- `status`

---
## 1.3 Example DDL for Fact & Dimensions (PostgreSQL)

```sql
CREATE SCHEMA IF NOT EXISTS dw;

CREATE TABLE dw.dim_date (
    date_key     INTEGER PRIMARY KEY,
    date         DATE NOT NULL,
    year         INTEGER,
    quarter      INTEGER,
    month        INTEGER,
    day          INTEGER,
    weekday      INTEGER,
    is_weekend   BOOLEAN
);

CREATE TABLE dw.dim_county AS
SELECT
    id AS county_id,
    state_code,
    county_name,
    auction_type,
    timezone
FROM counties;

ALTER TABLE dw.dim_county ADD PRIMARY KEY (county_id);

CREATE TABLE dw.dim_property AS
SELECT
    p.id AS property_id,
    p.county_id,
    p.apn,
    p.street_address,
    p.city,
    p.state,
    p.zip_code,
    p.property_type,
    p.land_sqft,
    p.building_sqft,
    p.year_built,
    p.zoning
FROM properties p;

ALTER TABLE dw.dim_property ADD PRIMARY KEY (property_id);

CREATE TABLE dw.dim_lien AS
SELECT
    l.id AS lien_id,
    l.property_id,
    pr.county_id,
    l.lien_certificate_number,
    l.lien_type,
    l.interest_rate_nominal,
    l.interest_type,
    l.redemption_period_months,
    l.issue_date,
    l.redemption_deadline
FROM liens l
JOIN properties pr ON pr.id = l.property_id;

ALTER TABLE dw.dim_lien ADD PRIMARY KEY (lien_id);

CREATE TABLE dw.dim_investor AS
SELECT
    ip.id AS investor_profile_id,
    ip.user_id,
    ip.display_name,
    ip.strategy_type,
    ip.min_target_yield,
    ip.max_risk_score,
    ip.time_horizon_months
FROM investor_profiles ip;

ALTER TABLE dw.dim_investor ADD PRIMARY KEY (investor_profile_id);

CREATE TABLE dw.dim_analysis_run AS
SELECT
    ar.id AS analysis_run_id,
    ar.analysis_type,
    CAST(to_char(ar.created_at::date, 'YYYYMMDD') AS INTEGER) AS analysis_date_key,
    ar.target_county_id,
    ar.status
FROM analysis_runs ar;

ALTER TABLE dw.dim_analysis_run ADD PRIMARY KEY (analysis_run_id);

CREATE TABLE dw.fact_lien_analysis (
    fact_id                         BIGSERIAL PRIMARY KEY,
    analysis_run_id                 BIGINT NOT NULL,
    lien_id                         BIGINT NOT NULL,
    property_id                     BIGINT NOT NULL,
    county_id                       BIGINT NOT NULL,
    investor_profile_id             BIGINT,
    portfolio_id                    BIGINT,
    analysis_date_key               INTEGER NOT NULL,

    lien_principal_amount           NUMERIC(18,2),
    avm_value                       NUMERIC(18,2),
    lien_to_value_ratio             NUMERIC(8,4),
    estimated_redemption_hold_months NUMERIC(8,2),
    simple_yield                    NUMERIC(10,4),
    annualized_yield                NUMERIC(10,4),
    cash_on_cash_return             NUMERIC(10,4),
    irr_redemption_scenario         NUMERIC(10,4),
    irr_deed_scenario               NUMERIC(10,4),
    expected_value_overall          NUMERIC(18,4),

    title_risk_score                NUMERIC(6,3),
    structural_risk_score           NUMERIC(6,3),
    neighborhood_risk_score         NUMERIC(6,3),
    vacancy_risk_score              NUMERIC(6,3),
    overall_risk_score              NUMERIC(6,3),

    prob_redemption                 NUMERIC(5,4),
    prob_deed_conversion            NUMERIC(5,4),
    prob_assignment                 NUMERIC(5,4),
    proj_profit_redemption          NUMERIC(18,4),
    proj_profit_deed                NUMERIC(18,4),
    proj_profit_assignment          NUMERIC(18,4),

    composite_score                 NUMERIC(6,3),
    yield_score                     NUMERIC(6,3),
    risk_adjusted_return_score      NUMERIC(6,3),
    liquidity_score                 NUMERIC(6,3),
    strategy_fit_score              NUMERIC(6,3)
);
```

Population of `fact_lien_analysis` is typically done via **ETL/ELT jobs** that join OLTP tables (`deal_metrics`, `risk_assessments`, `scenario_analyses`, `deal_scores`, `liens`, `properties`, `analysis_runs`, etc.).

---
# 2. Materialized Views for Analytics

These materialized views provide pre-aggregated insights for dashboards and BI.

## 2.1 MV – Yield & Risk by County

```sql
CREATE MATERIALIZED VIEW dw.mv_county_yield_risk AS
SELECT
    f.county_id,
    c.state_code,
    c.county_name,
    COUNT(*)                                   AS lien_count,
    AVG(f.annualized_yield)                   AS avg_annualized_yield,
    AVG(f.overall_risk_score)                 AS avg_overall_risk_score,
    AVG(f.expected_value_overall)             AS avg_expected_value,
    SUM(f.expected_value_overall)             AS total_expected_value
FROM dw.fact_lien_analysis f
JOIN dw.dim_county c ON c.county_id = f.county_id
GROUP BY f.county_id, c.state_code, c.county_name;

-- Index for fast refresh and queries
CREATE INDEX ON dw.mv_county_yield_risk (state_code, county_name);
```

## 2.2 MV – Investor Portfolio Performance

```sql
CREATE MATERIALIZED VIEW dw.mv_investor_portfolio_perf AS
SELECT
    ip.investor_profile_id,
    ip.display_name,
    p.id AS portfolio_id,
    p.name AS portfolio_name,
    COUNT(ph.id)                      AS holding_count,
    SUM(ph.acquisition_price)         AS total_invested,
    SUM(COALESCE(ph.disposition_proceeds,0) + COALESCE(ph.redemption_amount_received,0)) AS total_return,
    SUM(COALESCE(ph.disposition_proceeds,0) + COALESCE(ph.redemption_amount_received,0))
      - SUM(ph.acquisition_price)     AS total_profit,
    CASE WHEN SUM(ph.acquisition_price) > 0 THEN
        (SUM(COALESCE(ph.disposition_proceeds,0) + COALESCE(ph.redemption_amount_received,0))
        - SUM(ph.acquisition_price)) / SUM(ph.acquisition_price)
    ELSE NULL END                     AS gross_roi
FROM portfolios p
JOIN investor_profiles ip ON ip.id = p.investor_profile_id
JOIN portfolio_holdings ph ON ph.portfolio_id = p.id
GROUP BY ip.investor_profile_id, ip.display_name, p.id, p.name;

CREATE INDEX ON dw.mv_investor_portfolio_perf (investor_profile_id);
```

## 2.3 MV – Strategy Performance Over Time

```sql
CREATE MATERIALIZED VIEW dw.mv_strategy_performance AS
SELECT
    d.year,
    d.month,
    inv.strategy_type,
    COUNT(DISTINCT f.analysis_run_id)         AS analysis_runs,
    AVG(f.composite_score)                    AS avg_composite_score,
    AVG(f.annualized_yield)                   AS avg_annualized_yield,
    AVG(f.overall_risk_score)                 AS avg_risk_score
FROM dw.fact_lien_analysis f
JOIN dw.dim_analysis_run ar ON ar.analysis_run_id = f.analysis_run_id
JOIN dw.dim_date d ON d.date_key = ar.analysis_date_key
LEFT JOIN dw.dim_investor inv ON inv.investor_profile_id = f.investor_profile_id
GROUP BY d.year, d.month, inv.strategy_type;

CREATE INDEX ON dw.mv_strategy_performance (year, month, strategy_type);
```

**Refresh strategy:**
- Use `REFRESH MATERIALIZED VIEW CONCURRENTLY ...` on a schedule (e.g., hourly, nightly), depending on volume and freshness requirements.

---
# 3. Time-Series Models for Forecasting

Goal: forecast key metrics such as:
- **Future redemptions** (count and cash inflow)
- **Expected portfolio value** over time
- **County-level yield trends**

## 3.1 Time-Series Tables

### 3.1.1 `ts_redemption_cashflows`
Aggregated daily redemption cashflows.

```sql
CREATE TABLE dw.ts_redemption_cashflows AS
SELECT
    CAST(to_char(COALESCE(ph.redemption_date, ph.disposition_date), 'YYYYMMDD') AS INTEGER) AS date_key,
    COALESCE(ph.redemption_date, ph.disposition_date)::date AS date,
    SUM(COALESCE(ph.redemption_amount_received,0) + COALESCE(ph.disposition_proceeds,0)) AS cashflow
FROM portfolio_holdings ph
WHERE ph.redemption_amount_received IS NOT NULL OR ph.disposition_proceeds IS NOT NULL
GROUP BY date_key, date;

ALTER TABLE dw.ts_redemption_cashflows ADD PRIMARY KEY (date_key);
```

This table can be periodically rebuilt or incrementally updated.

## 3.2 Forecasting Approach

You can attach a modeling layer in Python (or db-native ML if using something like BigQuery ML), e.g.:

- Models: **ARIMA**, **Prophet**, **Exponential Smoothing**, or **LSTM** (if you want deep learning)
- Target: `cashflow` per day/week/month

### 3.2.1 Example Python Pseudocode (Prophet-style)

```python
import pandas as pd
from prophet import Prophet
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://user:pass@host/db")

df = pd.read_sql("SELECT date AS ds, cashflow AS y FROM dw.ts_redemption_cashflows ORDER BY date", engine)

m = Prophet()
m.fit(df)

future = m.make_future_dataframe(periods=180)  # forecast 6 months
forecast = m.predict(future)

# Write forecast back to DB
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_sql(
    'ts_redemption_cashflows_forecast',
    engine,
    schema='dw',
    if_exists='replace',
    index=False,
)
```

### 3.2.2 Forecast Table

```sql
CREATE TABLE dw.ts_redemption_cashflows_forecast (
    date        DATE PRIMARY KEY,
    yhat        NUMERIC(18,4),
    yhat_lower  NUMERIC(18,4),
    yhat_upper  NUMERIC(18,4)
);
```

You can repeat similar patterns for:
- `ts_county_yield` – average yield per county per month
- `ts_portfolio_value` – cumulative portfolio value per investor over time

---
# 4. Summary

These analytical extensions give you:

- A robust **star-schema** for BI and dashboards
- **Materialized views** for fast, pre-aggregated insights
- A **time-series foundation** for forecasting redemptions, portfolio performance, and county-level yield trends

They sit cleanly on top of the OLTP schema and can be implemented incrementally (start with `fact_lien_analysis` and a couple of dimensions, then layer in MVs and time-series tables as data volume and reporting complexity grow).

---
**End of Analytical Extensions**
# Implementation Artifacts – Tax Lien Strategist App

This document provides concrete implementation artifacts for the previously defined data model, assuming **PostgreSQL** as the primary database and **SQLAlchemy** (Python) as the ORM.

Contents:
1. PostgreSQL `CREATE TABLE` schema (core tables)
2. SQLAlchemy ORM model skeletons

---
## 1. PostgreSQL Schema (DDL)

> Note: This DDL assumes:
> - PostgreSQL 14+
> - `uuid-ossp` extension (optional if using UUIDs)
> - `jsonb` support
> - Application-level enforcement of enums (or create enum types beforehand)

You can adapt IDs to `UUID` if preferred; here we’ll use `BIGSERIAL` for clarity.

```sql
-- Enable extensions as needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Core Users & Investor Profiles

CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    role            VARCHAR(32) NOT NULL CHECK (role IN ('investor', 'admin', 'analyst')),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE investor_profiles (
    id                         BIGSERIAL PRIMARY KEY,
    user_id                    BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    display_name               VARCHAR(255) NOT NULL,
    investment_budget_total    NUMERIC(18,2),
    min_target_yield           NUMERIC(6,3),
    max_risk_score             NUMERIC(6,3),
    preferred_states           TEXT, -- could store comma-separated or JSON array
    time_horizon_months        INTEGER,
    strategy_type              VARCHAR(32) CHECK (strategy_type IN ('yield', 'equity', 'balanced')),
    created_at                 TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                 TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Jurisdictions, Properties & Liens

CREATE TABLE counties (
    id              BIGSERIAL PRIMARY KEY,
    state_code      VARCHAR(2) NOT NULL,
    county_name     VARCHAR(255) NOT NULL,
    auction_type    VARCHAR(32) NOT NULL CHECK (auction_type IN ('tax_lien', 'tax_deed', 'hybrid')),
    timezone        VARCHAR(64),
    data_source_url TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (state_code, county_name)
);

CREATE TABLE properties (
    id              BIGSERIAL PRIMARY KEY,
    county_id       BIGINT NOT NULL REFERENCES counties(id) ON DELETE CASCADE,
    apn             VARCHAR(128) NOT NULL,
    street_address  TEXT,
    city            VARCHAR(255),
    state           VARCHAR(2),
    zip_code        VARCHAR(16),
    lat             NUMERIC(10,7),
    lng             NUMERIC(10,7),
    property_type   VARCHAR(32) CHECK (property_type IN ('sfh','mfh','land','commercial','industrial','mixed_use','other')),
    land_sqft       NUMERIC(14,2),
    building_sqft   NUMERIC(14,2),
    year_built      INTEGER,
    zoning          VARCHAR(128),
    last_updated_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (county_id, apn)
);

CREATE TABLE auctions (
    id              BIGSERIAL PRIMARY KEY,
    county_id       BIGINT NOT NULL REFERENCES counties(id) ON DELETE CASCADE,
    auction_name    VARCHAR(255),
    auction_date    DATE NOT NULL,
    auction_type    VARCHAR(32) CHECK (auction_type IN ('in_person','online','hybrid')),
    source_url      TEXT,
    status          VARCHAR(32) NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled','completed','canceled')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE liens (
    id                       BIGSERIAL PRIMARY KEY,
    property_id              BIGINT NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    auction_id               BIGINT REFERENCES auctions(id) ON DELETE SET NULL,
    lien_certificate_number  VARCHAR(255),
    lien_type                VARCHAR(32) NOT NULL CHECK (lien_type IN ('tax_lien','tax_deed','other')),
    lien_principal_amount    NUMERIC(18,2) NOT NULL,
    interest_rate_nominal    NUMERIC(8,4),
    interest_type            VARCHAR(32) CHECK (interest_type IN ('simple','penalty','compound','stepped')),
    redemption_period_months INTEGER,
    issue_date               DATE,
    redemption_deadline      DATE,
    status                   VARCHAR(32) NOT NULL DEFAULT 'available' CHECK (status IN ('available','sold','redeemed','foreclosed','canceled')),
    current_holder           VARCHAR(255),
    created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at               TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Market & Valuation Data

CREATE TABLE property_valuations (
    id               BIGSERIAL PRIMARY KEY,
    property_id      BIGINT NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    valuation_date   DATE NOT NULL,
    avm_value        NUMERIC(18,2),
    low_value        NUMERIC(18,2),
    high_value       NUMERIC(18,2),
    valuation_source VARCHAR(32) CHECK (valuation_source IN ('mls','zillow','attom','internal_model')),
    confidence_score NUMERIC(5,3),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE property_comps (
    id                     BIGSERIAL PRIMARY KEY,
    property_id            BIGINT NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    comp_property_address  TEXT,
    comp_sale_price        NUMERIC(18,2),
    comp_sale_date         DATE,
    distance_miles         NUMERIC(8,3),
    similarity_score       NUMERIC(5,3),
    source                 VARCHAR(64),
    created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Analysis & Scenario Modeling

CREATE TABLE analysis_runs (
    id                     BIGSERIAL PRIMARY KEY,
    investor_profile_id    BIGINT REFERENCES investor_profiles(id) ON DELETE SET NULL,
    initiated_by_user_id   BIGINT REFERENCES users(id) ON DELETE SET NULL,
    analysis_type          VARCHAR(32) NOT NULL CHECK (analysis_type IN ('county_batch','portfolio_rebalance','single_lien','watchlist_refresh')),
    target_county_id       BIGINT REFERENCES counties(id) ON DELETE SET NULL,
    status                 VARCHAR(32) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','running','completed','failed')),
    started_at             TIMESTAMPTZ,
    completed_at           TIMESTAMPTZ,
    error_message          TEXT,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE deal_metrics (
    id                               BIGSERIAL PRIMARY KEY,
    analysis_run_id                  BIGINT NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
    lien_id                          BIGINT NOT NULL REFERENCES liens(id) ON DELETE CASCADE,
    property_id                      BIGINT NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    valuation_id                     BIGINT REFERENCES property_valuations(id) ON DELETE SET NULL,
    lien_to_value_ratio              NUMERIC(8,4),
    estimated_redemption_hold_months NUMERIC(8,2),
    simple_yield                     NUMERIC(10,4),
    annualized_yield                 NUMERIC(10,4),
    cash_on_cash_return              NUMERIC(10,4),
    irr_redemption_scenario          NUMERIC(10,4),
    irr_deed_scenario                NUMERIC(10,4),
    expected_value_overall           NUMERIC(18,4),
    liquidity_score                  NUMERIC(6,3),
    created_at                       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE risk_assessments (
    id                           BIGSERIAL PRIMARY KEY,
    analysis_run_id              BIGINT NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
    lien_id                      BIGINT NOT NULL REFERENCES liens(id) ON DELETE CASCADE,
    property_id                  BIGINT NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    title_risk_score             NUMERIC(6,3),
    structural_risk_score        NUMERIC(6,3),
    neighborhood_risk_score      NUMERIC(6,3),
    vacancy_risk_score           NUMERIC(6,3),
    legal_complexity_risk_score  NUMERIC(6,3),
    overall_risk_score           NUMERIC(6,3),
    risk_flags                   JSONB,
    created_at                   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE scenario_analyses (
    id                      BIGSERIAL PRIMARY KEY,
    analysis_run_id         BIGINT NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
    lien_id                 BIGINT NOT NULL REFERENCES liens(id) ON DELETE CASCADE,
    scenario_type           VARCHAR(32) NOT NULL CHECK (scenario_type IN ('redemption','deed_conversion','assignment_resell')),
    probability             NUMERIC(5,4),
    projected_profit        NUMERIC(18,4),
    projected_roi           NUMERIC(10,4),
    projected_irr           NUMERIC(10,4),
    holding_period_months   NUMERIC(8,2),
    total_capital_required  NUMERIC(18,2),
    notes                   TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE deal_scores (
    id                           BIGSERIAL PRIMARY KEY,
    analysis_run_id              BIGINT NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
    investor_profile_id          BIGINT NOT NULL REFERENCES investor_profiles(id) ON DELETE CASCADE,
    lien_id                      BIGINT NOT NULL REFERENCES liens(id) ON DELETE CASCADE,
    composite_score              NUMERIC(6,3),
    yield_score                  NUMERIC(6,3),
    risk_adjusted_return_score   NUMERIC(6,3),
    liquidity_score              NUMERIC(6,3),
    strategy_fit_score           NUMERIC(6,3),
    rank_within_run              INTEGER,
    created_at                   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. Portfolios

CREATE TABLE portfolios (
    id                  BIGSERIAL PRIMARY KEY,
    investor_profile_id BIGINT NOT NULL REFERENCES investor_profiles(id) ON DELETE CASCADE,
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE portfolio_holdings (
    id                          BIGSERIAL PRIMARY KEY,
    portfolio_id                BIGINT NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    lien_id                     BIGINT NOT NULL REFERENCES liens(id) ON DELETE CASCADE,
    acquisition_date            DATE,
    acquisition_price           NUMERIC(18,2),
    current_status              VARCHAR(32) NOT NULL CHECK (current_status IN ('held','redeemed','foreclosed','sold_assignment','written_off')),
    redemption_amount_received  NUMERIC(18,2),
    foreclosure_date            DATE,
    disposition_date            DATE,
    disposition_proceeds        NUMERIC(18,2),
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. AGI / Agent Operations

CREATE TABLE agent_tasks (
    id                    BIGSERIAL PRIMARY KEY,
    analysis_run_id       BIGINT REFERENCES analysis_runs(id) ON DELETE SET NULL,
    parent_task_id        BIGINT REFERENCES agent_tasks(id) ON DELETE SET NULL,
    agent_type            VARCHAR(32) NOT NULL CHECK (agent_type IN ('orchestrator','research','underwriting','document')),
    task_name             VARCHAR(255) NOT NULL,
    status                VARCHAR(32) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','in_progress','completed','failed')),
    input_payload         JSONB,
    output_payload        JSONB,
    error_message         TEXT,
    started_at            TIMESTAMPTZ,
    completed_at          TIMESTAMPTZ,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE agent_logs (
    id             BIGSERIAL PRIMARY KEY,
    agent_task_id  BIGINT NOT NULL REFERENCES agent_tasks(id) ON DELETE CASCADE,
    log_type       VARCHAR(32) NOT NULL CHECK (log_type IN ('plan','step','error','summary')),
    content        TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE embeddings (
    id             BIGSERIAL PRIMARY KEY,
    entity_type    VARCHAR(64) NOT NULL,
    entity_id      BIGINT NOT NULL,
    embedding_vector BYTEA NOT NULL,
    model_name     VARCHAR(128),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. Documents & Notifications

CREATE TABLE documents (
    id                         BIGSERIAL PRIMARY KEY,
    owner_user_id              BIGINT REFERENCES users(id) ON DELETE SET NULL,
    portfolio_id               BIGINT REFERENCES portfolios(id) ON DELETE SET NULL,
    analysis_run_id            BIGINT REFERENCES analysis_runs(id) ON DELETE SET NULL,
    lien_id                    BIGINT REFERENCES liens(id) ON DELETE SET NULL,
    document_type              VARCHAR(64) NOT NULL,
    storage_url                TEXT NOT NULL,
    mime_type                  VARCHAR(128),
    generated_by_agent_task_id BIGINT REFERENCES agent_tasks(id) ON DELETE SET NULL,
    created_at                 TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE notifications (
    id                  BIGSERIAL PRIMARY KEY,
    user_id             BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_type   VARCHAR(64) NOT NULL,
    title               VARCHAR(255) NOT NULL,
    body                TEXT NOT NULL,
    metadata            JSONB,
    is_read             BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    read_at             TIMESTAMPTZ
);

-- 8. Integration & Audit

CREATE TABLE integration_events (
    id               BIGSERIAL PRIMARY KEY,
    source_system    VARCHAR(64) NOT NULL,
    request_payload  JSONB,
    response_payload JSONB,
    status           VARCHAR(32) NOT NULL CHECK (status IN ('success','failed')),
    error_message    TEXT,
    started_at       TIMESTAMPTZ,
    completed_at     TIMESTAMPTZ
);

CREATE TABLE audit_logs (
    id           BIGSERIAL PRIMARY KEY,
    user_id      BIGINT REFERENCES users(id) ON DELETE SET NULL,
    event_type   VARCHAR(64) NOT NULL,
    entity_type  VARCHAR(64) NOT NULL,
    entity_id    BIGINT,
    description  TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---
## 2. SQLAlchemy ORM Model Skeletons (Python)

> Note: This is a **skeleton**, not every field or relationship is shown to keep the code readable. It’s intended as a starting point.

```python
from datetime import datetime
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Date, DateTime, Boolean,
    Numeric, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    investor_profiles = relationship("InvestorProfile", back_populates="user")
    notifications = relationship("Notification", back_populates="user")


class InvestorProfile(Base):
    __tablename__ = "investor_profiles"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    display_name = Column(String(255), nullable=False)
    investment_budget_total = Column(Numeric(18, 2))
    min_target_yield = Column(Numeric(6, 3))
    max_risk_score = Column(Numeric(6, 3))
    preferred_states = Column(Text)
    time_horizon_months = Column(Integer)
    strategy_type = Column(String(32))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="investor_profiles")
    portfolios = relationship("Portfolio", back_populates="investor_profile")


class County(Base):
    __tablename__ = "counties"

    id = Column(BigInteger, primary_key=True)
    state_code = Column(String(2), nullable=False)
    county_name = Column(String(255), nullable=False)
    auction_type = Column(String(32), nullable=False)
    timezone = Column(String(64))
    data_source_url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    properties = relationship("Property", back_populates="county")
    auctions = relationship("Auction", back_populates="county")


class Property(Base):
    __tablename__ = "properties"

    id = Column(BigInteger, primary_key=True)
    county_id = Column(BigInteger, ForeignKey("counties.id"), nullable=False)
    apn = Column(String(128), nullable=False)
    street_address = Column(Text)
    city = Column(String(255))
    state = Column(String(2))
    zip_code = Column(String(16))
    lat = Column(Numeric(10, 7))
    lng = Column(Numeric(10, 7))
    property_type = Column(String(32))
    land_sqft = Column(Numeric(14, 2))
    building_sqft = Column(Numeric(14, 2))
    year_built = Column(Integer)
    zoning = Column(String(128))
    last_updated_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    county = relationship("County", back_populates="properties")
    liens = relationship("Lien", back_populates="property")


class Auction(Base):
    __tablename__ = "auctions"

    id = Column(BigInteger, primary_key=True)
    county_id = Column(BigInteger, ForeignKey("counties.id"), nullable=False)
    auction_name = Column(String(255))
    auction_date = Column(Date, nullable=False)
    auction_type = Column(String(32))
    source_url = Column(Text)
    status = Column(String(32), default="scheduled", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    county = relationship("County", back_populates="auctions")
    liens = relationship("Lien", back_populates="auction")


class Lien(Base):
    __tablename__ = "liens"

    id = Column(BigInteger, primary_key=True)
    property_id = Column(BigInteger, ForeignKey("properties.id"), nullable=False)
    auction_id = Column(BigInteger, ForeignKey("auctions.id"))
    lien_certificate_number = Column(String(255))
    lien_type = Column(String(32), nullable=False)
    lien_principal_amount = Column(Numeric(18, 2), nullable=False)
    interest_rate_nominal = Column(Numeric(8, 4))
    interest_type = Column(String(32))
    redemption_period_months = Column(Integer)
    issue_date = Column(Date)
    redemption_deadline = Column(Date)
    status = Column(String(32), default="available", nullable=False)
    current_holder = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    property = relationship("Property", back_populates="liens")
    auction = relationship("Auction", back_populates="liens")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(BigInteger, primary_key=True)
    investor_profile_id = Column(BigInteger, ForeignKey("investor_profiles.id"))
    initiated_by_user_id = Column(BigInteger, ForeignKey("users.id"))
    analysis_type = Column(String(32), nullable=False)
    target_county_id = Column(BigInteger, ForeignKey("counties.id"))
    status = Column(String(32), default="pending", nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    deal_metrics = relationship("DealMetric", back_populates="analysis_run")


class DealMetric(Base):
    __tablename__ = "deal_metrics"

    id = Column(BigInteger, primary_key=True)
    analysis_run_id = Column(BigInteger, ForeignKey("analysis_runs.id"), nullable=False)
    lien_id = Column(BigInteger, ForeignKey("liens.id"), nullable=False)
    property_id = Column(BigInteger, ForeignKey("properties.id"), nullable=False)

    lien_to_value_ratio = Column(Numeric(8, 4))
    simple_yield = Column(Numeric(10, 4))
    annualized_yield = Column(Numeric(10, 4))

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    analysis_run = relationship("AnalysisRun", back_populates="deal_metrics")


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(BigInteger, primary_key=True)
    investor_profile_id = Column(BigInteger, ForeignKey("investor_profiles.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    investor_profile = relationship("InvestorProfile", back_populates="portfolios")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    notification_type = Column(String(64), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    metadata = Column(JSON)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime)

    user = relationship("User", back_populates="notifications")
```

You can extend these ORM classes to cover all remaining tables (`risk_assessments`, `scenario_analyses`, `deal_scores`, `agent_tasks`, etc.) using the same patterns shown above.

---

This file now contains the **core implementation artifacts** for the data model:
- Executable PostgreSQL schema
- ORM skeleton for Python/SQLAlchemy

You can plug this into your backend service and incrementally refine constraints, indexes, and relationships based on performance profiling and query patterns.


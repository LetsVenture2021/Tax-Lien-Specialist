"""Enumerations for domain-specific column constraints."""

from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    INVESTOR = "investor"
    ADMIN = "admin"
    ANALYST = "analyst"


class StrategyType(str, Enum):
    YIELD = "yield"
    EQUITY = "equity"
    BALANCED = "balanced"


class CountyAuctionType(str, Enum):
    TAX_LIEN = "tax_lien"
    TAX_DEED = "tax_deed"
    HYBRID = "hybrid"


class AuctionSaleType(str, Enum):
    IN_PERSON = "in_person"
    ONLINE = "online"
    HYBRID = "hybrid"


class LienType(str, Enum):
    TAX_LIEN = "tax_lien"
    TAX_DEED = "tax_deed"
    OTHER = "other"


class InterestType(str, Enum):
    SIMPLE = "simple"
    PENALTY = "penalty"
    COMPOUND = "compound"
    STEPPED = "stepped"


class LienStatus(str, Enum):
    AVAILABLE = "available"
    SOLD = "sold"
    REDEEMED = "redeemed"
    FORECLOSED = "foreclosed"
    CANCELED = "canceled"


class PropertyType(str, Enum):
    SINGLE_FAMILY = "sfh"
    MULTI_FAMILY = "mfh"
    LAND = "land"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    MIXED_USE = "mixed_use"
    OTHER = "other"


class AnalysisType(str, Enum):
    COUNTY_BATCH = "county_batch"
    PORTFOLIO_REBALANCE = "portfolio_rebalance"
    SINGLE_LIEN = "single_lien"
    WATCHLIST_REFRESH = "watchlist_refresh"


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScenarioType(str, Enum):
    REDEMPTION = "redemption"
    DEED_CONVERSION = "deed_conversion"
    ASSIGNMENT_RESELL = "assignment_resell"


class PortfolioHoldingStatus(str, Enum):
    HELD = "held"
    REDEEMED = "redeemed"
    FORECLOSED = "foreclosed"
    SOLD_ASSIGNMENT = "sold_assignment"
    WRITTEN_OFF = "written_off"


class AgentType(str, Enum):
    ORCHESTRATOR = "orchestrator"
    RESEARCH = "research"
    UNDERWRITING = "underwriting"
    DOCUMENT = "document"


class AgentTaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentLogType(str, Enum):
    PLAN = "plan"
    STEP = "step"
    ERROR = "error"
    SUMMARY = "summary"


class DocumentType(str, Enum):
    INVESTOR_SUMMARY = "investor_summary"
    PROMISSORY_NOTE = "promissory_note"
    FORECLOSURE_PACKET = "foreclosure_packet"
    PORTFOLIO_REPORT = "portfolio_report"
    OTHER = "other"


class IntegrationSource(str, Enum):
    COUNTY = "county"
    MLS = "mls"
    GIS = "gis"
    AUCTION_PLATFORM = "auction_platform"
    OTHER = "other"


class IntegrationStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"


class NotificationType(str, Enum):
    GENERAL = "general"
    WORKFLOW = "workflow"
    PORTFOLIO = "portfolio"
    ALERT = "alert"

```
"""Pydantic models defining request/response contracts for agent tool endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


class DateRange(BaseModel):
    """Optional window used by ingestion tools when restricting lien batches."""

    start: Optional[datetime] = None
    end: Optional[datetime] = None


class FetchCountyLiensRequest(BaseModel):
    """Input payload for the `fetch_county_liens` tool contract."""

    county_id: int
    date_range: Optional[DateRange] = None


class FetchCountyLiensResponse(BaseModel):
    """Minimal response contract for lien ingestion requests."""

    items: List[Dict[str, Any]] = Field(default_factory=list)
    total: int = 0


class FetchPropertyDetailsRequest(BaseModel):
    """Input payload for `fetch_property_details`."""

    property_id: int


class FetchPropertyDetailsResponse(BaseModel):
    """Property metadata and the most recent valuation payload."""

    property: Dict[str, Any]
    valuation: Optional[Dict[str, Any]] = None


class ComputeLienMetricsRequest(BaseModel):
    """Input payload for computing normalized risk metrics."""

    lien_id: int


class ComputeLienMetricsResponse(BaseModel):
    """Calculated metrics surfaced to the underwriting agent."""

    model_config = ConfigDict(populate_by_name=True)

    yield_rate: float = Field(alias="yield")
    ltv: float
    risk_score: float
    deal_score: float


class GenerateDocumentFromTemplateRequest(BaseModel):
    """Input payload for document generation requests."""

    template_key: str
    context: Dict[str, Any]


class GenerateDocumentFromTemplateResponse(BaseModel):
    """Result payload returned when the document agent produces an artifact."""

    document_id: int
    status: str


class UpdateAnalysisRunStatusRequest(BaseModel):
    """State mutation contract for analysis runs orchestrated by agents."""

    analysis_run_id: int
    status: str
    summary: Optional[str] = None


class LogDecisionEventRequest(BaseModel):
    """Structured decision payload recorded for reasoning explorer telemetry."""

    episode_id: int
    agent_task_id: int
    decision_type: str
    payload: Dict[str, Any]


class LogDecisionEventResponse(BaseModel):
    """Acknowledgement returned when a decision entry is persisted."""

    id: int
    episode_id: int
    agent_task_id: int
    decision_type: str
    created_at: datetime
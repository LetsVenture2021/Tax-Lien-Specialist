"""Analysis and scoring models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID as PyUUID

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.enums import AnalysisStatus, AnalysisType, ScenarioType
from app.models.mixins import BaseModel, TimestampMixin

if TYPE_CHECKING:  # pragma: no cover
    from app.models.geography import County
    from app.models.lien import Lien
    from app.models.portfolio import Portfolio
    from app.models.user import InvestorProfile, User


class AnalysisRun(TimestampMixin, BaseModel):
    __tablename__ = "analysis_runs"

    investor_profile_id: Mapped[Optional[PyUUID]] = mapped_column(
        ForeignKey("investor_profiles.id", ondelete="SET NULL"), nullable=True
    )
    initiated_by_user_id: Mapped[Optional[PyUUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    analysis_type: Mapped[AnalysisType] = mapped_column(Enum(AnalysisType, name="analysis_type"), nullable=False)
    target_county_id: Mapped[Optional[PyUUID]] = mapped_column(
        ForeignKey("counties.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[AnalysisStatus] = mapped_column(Enum(AnalysisStatus, name="analysis_status"), nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    investor_profile: Mapped[Optional["InvestorProfile"]] = relationship(back_populates="analysis_runs")
    initiated_by: Mapped[Optional["User"]] = relationship()
    target_county: Mapped[Optional["County"]] = relationship(back_populates="analysis_runs")
    deal_metrics: Mapped[list["DealMetric"]] = relationship(back_populates="analysis_run")
    risk_assessments: Mapped[list["RiskAssessment"]] = relationship(back_populates="analysis_run")
    scenario_analyses: Mapped[list["ScenarioAnalysis"]] = relationship(back_populates="analysis_run")
    deal_scores: Mapped[list["DealScore"]] = relationship(back_populates="analysis_run")
    agent_tasks: Mapped[list["AgentTask"]] = relationship(back_populates="analysis_run")
    documents: Mapped[list["Document"]] = relationship(back_populates="analysis_run")


class DealMetric(BaseModel):
    __tablename__ = "deal_metrics"

    analysis_run_id: Mapped[PyUUID] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False)
    lien_id: Mapped[PyUUID] = mapped_column(ForeignKey("liens.id", ondelete="CASCADE"), nullable=False)
    property_id: Mapped[PyUUID] = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    valuation_id: Mapped[Optional[PyUUID]] = mapped_column(ForeignKey("property_valuations.id", ondelete="SET NULL"))
    lien_to_value_ratio: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4))
    estimated_redemption_hold_months: Mapped[Optional[int]] = mapped_column(Integer)
    simple_yield: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 3))
    annualized_yield: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 3))
    cash_on_cash_return: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 3))
    irr_redemption_scenario: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 3))
    irr_deed_scenario: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 3))
    expected_value_overall: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    liquidity_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 3))

    analysis_run: Mapped["AnalysisRun"] = relationship(back_populates="deal_metrics")
    lien: Mapped["Lien"] = relationship(back_populates="deal_metrics")


class RiskAssessment(BaseModel):
    __tablename__ = "risk_assessments"

    analysis_run_id: Mapped[PyUUID] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False)
    lien_id: Mapped[PyUUID] = mapped_column(ForeignKey("liens.id", ondelete="CASCADE"), nullable=False)
    property_id: Mapped[PyUUID] = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    title_risk_score: Mapped[Optional[float]] = mapped_column(Float)
    structural_risk_score: Mapped[Optional[float]] = mapped_column(Float)
    neighborhood_risk_score: Mapped[Optional[float]] = mapped_column(Float)
    vacancy_risk_score: Mapped[Optional[float]] = mapped_column(Float)
    legal_complexity_risk_score: Mapped[Optional[float]] = mapped_column(Float)
    overall_risk_score: Mapped[Optional[float]] = mapped_column(Float)
    risk_flags: Mapped[Optional[dict]] = mapped_column(JSONB)

    analysis_run: Mapped["AnalysisRun"] = relationship(back_populates="risk_assessments")
    lien: Mapped["Lien"] = relationship(back_populates="risk_assessments")


class ScenarioAnalysis(BaseModel):
    __tablename__ = "scenario_analyses"

    analysis_run_id: Mapped[PyUUID] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False)
    lien_id: Mapped[PyUUID] = mapped_column(ForeignKey("liens.id", ondelete="CASCADE"), nullable=False)
    scenario_type: Mapped[ScenarioType] = mapped_column(
        Enum(ScenarioType, name="scenario_type"), nullable=False
    )
    probability: Mapped[Optional[float]] = mapped_column(Float)
    projected_profit: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    projected_roi: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 3))
    projected_irr: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 3))
    holding_period_months: Mapped[Optional[int]] = mapped_column(Integer)
    total_capital_required: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    analysis_run: Mapped["AnalysisRun"] = relationship(back_populates="scenario_analyses")
    lien: Mapped["Lien"] = relationship(back_populates="scenario_analyses")


class DealScore(BaseModel):
    __tablename__ = "deal_scores"

    analysis_run_id: Mapped[PyUUID] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False)
    investor_profile_id: Mapped[PyUUID] = mapped_column(ForeignKey("investor_profiles.id", ondelete="CASCADE"), nullable=False)
    lien_id: Mapped[PyUUID] = mapped_column(ForeignKey("liens.id", ondelete="CASCADE"), nullable=False)
    composite_score: Mapped[Optional[float]] = mapped_column(Float)
    yield_score: Mapped[Optional[float]] = mapped_column(Float)
    risk_adjusted_return_score: Mapped[Optional[float]] = mapped_column(Float)
    liquidity_score: Mapped[Optional[float]] = mapped_column(Float)
    strategy_fit_score: Mapped[Optional[float]] = mapped_column(Float)
    rank_within_run: Mapped[Optional[int]] = mapped_column(Integer)

    analysis_run: Mapped["AnalysisRun"] = relationship(back_populates="deal_scores")
    investor_profile: Mapped["InvestorProfile"] = relationship(back_populates="deal_scores")
    lien: Mapped["Lien"] = relationship(back_populates="deal_scores")

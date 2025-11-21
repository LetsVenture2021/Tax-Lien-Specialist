"""Lien-related models and associated analytics."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID as PyUUID

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.enums import InterestType, LienStatus, LienType
from app.models.mixins import BaseModel, TimestampMixin

if TYPE_CHECKING:  # pragma: no cover
    from app.models.analysis import AnalysisRun, DealMetric, RiskAssessment, ScenarioAnalysis, DealScore
    from app.models.geography import Auction, Property
    from app.models.portfolio import PortfolioHolding
    from app.models.notification import Document


class Lien(TimestampMixin, BaseModel):
    __tablename__ = "liens"

    property_id: Mapped[PyUUID] = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    auction_id: Mapped[Optional[PyUUID]] = mapped_column(ForeignKey("auctions.id", ondelete="SET NULL"))
    lien_certificate_number: Mapped[str] = mapped_column(String(128), nullable=False)
    lien_type: Mapped[LienType] = mapped_column(Enum(LienType, name="lien_type"), nullable=False)
    lien_principal_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    interest_rate_nominal: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    interest_type: Mapped[InterestType] = mapped_column(Enum(InterestType, name="interest_type"), nullable=False)
    redemption_period_months: Mapped[int] = mapped_column(Integer, nullable=False)
    issue_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    redemption_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[LienStatus] = mapped_column(Enum(LienStatus, name="lien_status"), nullable=False)
    current_holder: Mapped[Optional[str]] = mapped_column(String(255))

    property: Mapped["Property"] = relationship(back_populates="liens")
    auction: Mapped[Optional["Auction"]] = relationship(back_populates="liens")
    deal_metrics: Mapped[list["DealMetric"]] = relationship(back_populates="lien")
    risk_assessments: Mapped[list["RiskAssessment"]] = relationship(back_populates="lien")
    scenario_analyses: Mapped[list["ScenarioAnalysis"]] = relationship(back_populates="lien")
    deal_scores: Mapped[list["DealScore"]] = relationship(back_populates="lien")
    portfolio_holdings: Mapped[list["PortfolioHolding"]] = relationship(back_populates="lien")
    documents: Mapped[list["Document"]] = relationship(back_populates="lien")
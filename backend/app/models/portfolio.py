"""Portfolio management models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID as PyUUID

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.enums import PortfolioHoldingStatus
from app.models.mixins import BaseModel, TimestampMixin

if TYPE_CHECKING:  # pragma: no cover
    from app.models.analysis import AnalysisRun, DealScore
    from app.models.lien import Lien
    from app.models.notification import Document
    from app.models.user import InvestorProfile


class Portfolio(TimestampMixin, BaseModel):
    __tablename__ = "portfolios"

    investor_profile_id: Mapped[PyUUID] = mapped_column(
        ForeignKey("investor_profiles.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(512))

    investor_profile: Mapped["InvestorProfile"] = relationship(back_populates="portfolios")
    holdings: Mapped[list["PortfolioHolding"]] = relationship(back_populates="portfolio")
    documents: Mapped[list["Document"]] = relationship(back_populates="portfolio")


class PortfolioHolding(TimestampMixin, BaseModel):
    __tablename__ = "portfolio_holdings"

    portfolio_id: Mapped[PyUUID] = mapped_column(ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    lien_id: Mapped[PyUUID] = mapped_column(ForeignKey("liens.id", ondelete="CASCADE"), nullable=False)
    acquisition_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    acquisition_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    current_status: Mapped[PortfolioHoldingStatus] = mapped_column(
        Enum(PortfolioHoldingStatus, name="portfolio_holding_status"), nullable=False
    )
    redemption_amount_received: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    foreclosure_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    disposition_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    disposition_proceeds: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))

    portfolio: Mapped["Portfolio"] = relationship(back_populates="holdings")
    lien: Mapped["Lien"] = relationship(back_populates="portfolio_holdings")

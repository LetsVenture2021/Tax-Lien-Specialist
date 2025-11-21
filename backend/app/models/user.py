"""User and investor profile models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID as PyUUID

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.enums import StrategyType, UserRole
from app.models.mixins import BaseModel, TimestampMixin

if TYPE_CHECKING:  # pragma: no cover - imported for type checking only
    from app.models.analysis import AnalysisRun, DealScore
    from app.models.notification import Document, Notification
    from app.models.portfolio import Portfolio
    from app.models.system import AuditLog


class User(TimestampMixin, BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    investor_profile: Mapped["InvestorProfile"] = relationship(back_populates="user", uselist=False)
    documents: Mapped[list["Document"]] = relationship(back_populates="owner")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")


class InvestorProfile(TimestampMixin, BaseModel):
    __tablename__ = "investor_profiles"

    user_id: Mapped[PyUUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    investment_budget_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    min_target_yield: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    max_risk_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    preferred_states: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String(2)))
    time_horizon_months: Mapped[Optional[int]] = mapped_column(Integer)
    strategy_type: Mapped[StrategyType] = mapped_column(Enum(StrategyType, name="strategy_type"), nullable=False)

    user: Mapped[User] = relationship(back_populates="investor_profile")
    portfolios: Mapped[list["Portfolio"]] = relationship(back_populates="investor_profile")
    analysis_runs: Mapped[list["AnalysisRun"]] = relationship(back_populates="investor_profile")
    deal_scores: Mapped[list["DealScore"]] = relationship(back_populates="investor_profile")
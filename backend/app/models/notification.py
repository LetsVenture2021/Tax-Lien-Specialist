"""Document and notification models."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID as PyUUID

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.enums import DocumentType, NotificationType
from app.models.mixins import BaseModel, TimestampMixin

if TYPE_CHECKING:  # pragma: no cover
    from app.models.analysis import AnalysisRun
    from app.models.agent import AgentTask
    from app.models.lien import Lien
    from app.models.portfolio import Portfolio
    from app.models.user import User


class Document(TimestampMixin, BaseModel):
    __tablename__ = "documents"

    owner_user_id: Mapped[PyUUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    portfolio_id: Mapped[Optional[PyUUID]] = mapped_column(ForeignKey("portfolios.id", ondelete="SET NULL"))
    analysis_run_id: Mapped[Optional[PyUUID]] = mapped_column(ForeignKey("analysis_runs.id", ondelete="SET NULL"))
    lien_id: Mapped[Optional[PyUUID]] = mapped_column(ForeignKey("liens.id", ondelete="SET NULL"))
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType, name="document_type"), nullable=False
    )
    storage_url: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    generated_by_agent_task_id: Mapped[Optional[PyUUID]] = mapped_column(
        ForeignKey("agent_tasks.id", ondelete="SET NULL")
    )

    owner: Mapped["User"] = relationship(back_populates="documents")
    portfolio: Mapped[Optional["Portfolio"]] = relationship(back_populates="documents")
    analysis_run: Mapped[Optional["AnalysisRun"]] = relationship(back_populates="documents")
    lien: Mapped[Optional["Lien"]] = relationship(back_populates="documents")
    generated_by: Mapped[Optional["AgentTask"]] = relationship(back_populates="documents")


class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id: Mapped[PyUUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    notification_type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_type"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default="CURRENT_TIMESTAMP")
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="notifications")

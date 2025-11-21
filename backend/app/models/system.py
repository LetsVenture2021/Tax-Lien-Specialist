"""Integration and audit models."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.enums import IntegrationSource, IntegrationStatus
from app.models.mixins import BaseModel

if TYPE_CHECKING:  # pragma: no cover
    from app.models.user import User


class IntegrationEvent(BaseModel):
    __tablename__ = "integration_events"

    source_system: Mapped[IntegrationSource] = mapped_column(
        Enum(IntegrationSource, name="integration_source"), nullable=False
    )
    request_payload: Mapped[Optional[dict]] = mapped_column(JSONB)
    response_payload: Mapped[Optional[dict]] = mapped_column(JSONB)
    status: Mapped[IntegrationStatus] = mapped_column(
        Enum(IntegrationStatus, name="integration_status"), nullable=False
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[PyUUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    event_type: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default="CURRENT_TIMESTAMP")

    user: Mapped[Optional["User"]] = relationship(back_populates="audit_logs")

"""Agent task execution and logging models."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID as PyUUID

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.enums import AgentLogType, AgentTaskStatus, AgentType
from app.models.mixins import BaseModel, TimestampMixin

if TYPE_CHECKING:  # pragma: no cover
    from app.models.analysis import AnalysisRun
    from app.models.notification import Document


class AgentTask(TimestampMixin, BaseModel):
    __tablename__ = "agent_tasks"

    analysis_run_id: Mapped[Optional[PyUUID]] = mapped_column(
        ForeignKey("analysis_runs.id", ondelete="SET NULL"), nullable=True
    )
    parent_task_id: Mapped[Optional[PyUUID]] = mapped_column(ForeignKey("agent_tasks.id", ondelete="SET NULL"))
    agent_type: Mapped[AgentType] = mapped_column(Enum(AgentType, name="agent_type"), nullable=False)
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[AgentTaskStatus] = mapped_column(Enum(AgentTaskStatus, name="agent_task_status"), nullable=False)
    input_payload: Mapped[Optional[dict]] = mapped_column(JSONB)
    output_payload: Mapped[Optional[dict]] = mapped_column(JSONB)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    analysis_run: Mapped[Optional["AnalysisRun"]] = relationship(back_populates="agent_tasks")
    parent_task: Mapped[Optional["AgentTask"]] = relationship(remote_side="AgentTask.id")
    logs: Mapped[list["AgentLog"]] = relationship(back_populates="agent_task")
    documents: Mapped[list["Document"]] = relationship(back_populates="generated_by")


class AgentLog(BaseModel):
    __tablename__ = "agent_logs"

    agent_task_id: Mapped[PyUUID] = mapped_column(ForeignKey("agent_tasks.id", ondelete="CASCADE"), nullable=False)
    log_type: Mapped[AgentLogType] = mapped_column(Enum(AgentLogType, name="agent_log_type"), nullable=False)
    content: Mapped[dict | str] = mapped_column(JSONB)

    agent_task: Mapped["AgentTask"] = relationship(back_populates="logs")

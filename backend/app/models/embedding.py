"""Vector embedding storage model."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.models.mixins import BaseModel


class Embedding(BaseModel):
    __tablename__ = "embeddings"

    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding_vector: Mapped[list[float]] = mapped_column(Vector(1536))
    model_name: Mapped[Optional[str]] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default="CURRENT_TIMESTAMP")

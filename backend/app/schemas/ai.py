"""Pydantic models describing AI integration request and response payloads."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class TokenUsage(BaseModel):
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    reasoning_tokens: int | None = None


class TextGenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    model: str | None = None
    temperature: float = Field(default=0.2, ge=0, le=2)
    max_output_tokens: int | None = Field(default=None, gt=0)


class TextGenerationResponse(BaseModel):
    content: str
    model: str
    usage: Optional[TokenUsage] = None


class EmbeddingsRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1)
    model: str | None = None

    @field_validator("texts")
    @classmethod
    def ensure_non_empty_strings(cls, value: List[str]) -> List[str]:
        if any(not isinstance(text, str) or not text.strip() for text in value):
            raise ValueError("Texts must be non-empty strings.")
        return value


class EmbeddingsResponse(BaseModel):
    model: str
    embeddings: List[List[float]]
    usage: Optional[TokenUsage] = None


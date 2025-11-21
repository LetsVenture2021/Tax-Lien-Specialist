"""API routes that expose OpenAI-assisted capabilities."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from openai import OpenAIError

from app.ai.openai_service import OpenAIService
from app.api import deps
from app.schemas.ai import (
    EmbeddingsRequest,
    EmbeddingsResponse,
    TextGenerationRequest,
    TextGenerationResponse,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/responses", response_model=TextGenerationResponse)
async def create_text_response(
    payload: TextGenerationRequest,
    service: OpenAIService = Depends(deps.get_openai_service),
) -> TextGenerationResponse:
    try:
        result = await service.generate_text(
            prompt=payload.prompt,
            model=payload.model,
            temperature=payload.temperature,
            max_output_tokens=payload.max_output_tokens,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except OpenAIError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="OpenAI request failed.") from exc

    return TextGenerationResponse(**result)


@router.post("/embeddings", response_model=EmbeddingsResponse)
async def create_embeddings(
    payload: EmbeddingsRequest,
    service: OpenAIService = Depends(deps.get_openai_service),
) -> EmbeddingsResponse:
    try:
        result = await service.create_embeddings(texts=payload.texts, model=payload.model)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except OpenAIError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="OpenAI request failed.") from exc

    return EmbeddingsResponse(**result)


"""FastAPI dependency utilities (sessions, auth, pagination)."""

from typing import AsyncGenerator

from fastapi import HTTPException, status
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.openai_service import OpenAIService
from app.core.config import settings
from app.db.session import get_session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


async def get_openai_service() -> AsyncGenerator[OpenAIService, None]:
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="OpenAI API key not configured.")

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    service = OpenAIService(
        client=client,
        default_model=settings.OPENAI_MODEL_NAME,
        embedding_model=settings.OPENAI_EMBEDDING_MODEL,
    )
    try:
        yield service
    finally:
        await client.close()

"""Async helpers that wrap the OpenAI SDK for application workflows."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI


class OpenAIService:
    """Lightweight orchestration layer around the OpenAI Python client."""

    def __init__(self, client: AsyncOpenAI, default_model: str, embedding_model: str) -> None:
        self._client = client
        self._default_model = default_model
        self._embedding_model = embedding_model or "text-embedding-3-small"

    async def generate_text(
        self,
        prompt: str,
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_output_tokens: int | None = None,
    ) -> Dict[str, Any]:
        if not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        model_name = model or self._default_model
        request_payload: Dict[str, Any] = {
            "model": model_name,
            "input": prompt,
            "temperature": temperature,
        }
        if max_output_tokens is not None:
            request_payload["max_output_tokens"] = max_output_tokens

        response = await self._client.responses.create(**request_payload)
        if hasattr(response, "model_dump"):
            response_data = response.model_dump()
        else:
            response_data = {
                "output_text": getattr(response, "output_text", None),
                "output": getattr(response, "output", None),
            }
            usage_obj = getattr(response, "usage", None)
            if usage_obj is not None:
                if hasattr(usage_obj, "model_dump"):
                    response_data["usage"] = usage_obj.model_dump()
                elif isinstance(usage_obj, dict):
                    response_data["usage"] = usage_obj
        text = self._extract_text(response_data)
        if not text:
            raise RuntimeError("OpenAI response did not contain any text output.")

        usage = self._normalise_usage(response_data.get("usage"))
        return {"content": text, "model": model_name, "usage": usage}

    async def create_embeddings(
        self,
        texts: List[str],
        *,
        model: str | None = None,
    ) -> Dict[str, Any]:
        if not texts:
            raise ValueError("At least one text input is required for embeddings.")

        embedding_model = model or self._embedding_model
        response = await self._client.embeddings.create(model=embedding_model, input=texts)

        vectors: List[List[float]] = []
        for item in getattr(response, "data", []) or []:
            embedding = getattr(item, "embedding", None)
            if embedding is None and hasattr(item, "model_dump"):
                embedding = item.model_dump().get("embedding")
            if embedding is not None:
                vectors.append(list(embedding))

        if len(vectors) != len(texts):
            raise RuntimeError("OpenAI returned an unexpected number of embeddings.")

        usage_source: Optional[Any] = getattr(response, "usage", None)
        usage_data: Optional[Dict[str, Any]] = None
        if usage_source is not None:
            if hasattr(usage_source, "model_dump"):
                usage_data = usage_source.model_dump()
            elif isinstance(usage_source, dict):
                usage_data = usage_source

        usage = self._normalise_usage(usage_data)
        return {"embeddings": vectors, "model": embedding_model, "usage": usage}

    @staticmethod
    def _extract_text(response_data: Dict[str, Any]) -> str:
        if not isinstance(response_data, dict):
            return ""

        output_text = response_data.get("output_text")
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

        parts: List[str] = []
        for item in response_data.get("output", []) or []:
            content_items = item.get("content", []) if isinstance(item, dict) else []
            for block in content_items:
                if isinstance(block, dict) and block.get("type") in {"output_text", "text"}:
                    text_value = block.get("text")
                    if isinstance(text_value, str):
                        parts.append(text_value)
        return "".join(parts).strip()

    @staticmethod
    def _normalise_usage(usage: Optional[Dict[str, Any]]) -> Optional[Dict[str, int]]:
        if not usage:
            return None
        normalised: Dict[str, int] = {}
        for key in ("input_tokens", "output_tokens", "total_tokens", "reasoning_tokens"):
            value = usage.get(key)
            if isinstance(value, int):
                normalised[key] = value
        return normalised or None




























        



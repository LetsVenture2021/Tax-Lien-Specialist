from __future__ import annotations

from typing import Any, Dict, List, Optional

import pytest

from app.ai.openai_service import OpenAIService


class FakeResponseModel:
    def __init__(self, payload: Dict[str, Any]):
        self._payload = payload

    def model_dump(self) -> Dict[str, Any]:
        return self._payload


class FakeUsage:
    def __init__(self, payload: Dict[str, Any]):
        self._payload = payload

    def model_dump(self) -> Dict[str, Any]:
        return self._payload


class StubResponsesClient:
    def __init__(self, payload: Dict[str, Any]):
        self._payload = payload
        self.calls: List[Dict[str, Any]] = []

    async def create(self, **kwargs: Any) -> FakeResponseModel:
        self.calls.append(kwargs)
        return FakeResponseModel(self._payload)


class StubEmbeddingItem:
    def __init__(self, embedding: List[float]):
        self.embedding = embedding

    def model_dump(self) -> Dict[str, Any]:
        return {"embedding": self.embedding}


class StubEmbeddingsClient:
    def __init__(self, data: List[StubEmbeddingItem], usage: Optional[Dict[str, Any]] = None):
        self._data = data
        self._usage = FakeUsage(usage) if usage is not None else None
        self.calls: List[Dict[str, Any]] = []

    async def create(self, **kwargs: Any) -> "StubEmbeddingsResponse":
        self.calls.append(kwargs)
        return StubEmbeddingsResponse(self._data, self._usage)


class StubEmbeddingsResponse:
    def __init__(self, data: List[StubEmbeddingItem], usage: Optional[FakeUsage]):
        self.data = data
        self.usage = usage


class StubAsyncOpenAIClient:
    def __init__(self, responses_payload: Dict[str, Any], embeddings_payload: List[StubEmbeddingItem], usage: Optional[Dict[str, Any]] = None):
        self.responses = StubResponsesClient(responses_payload)
        self.embeddings = StubEmbeddingsClient(embeddings_payload, usage)

    async def close(self) -> None:  # pragma: no cover - mimics AsyncOpenAI.close
        return None


@pytest.mark.asyncio
async def test_generate_text_returns_expected_payload() -> None:
    payload = {
        "output_text": "hello world",
        "usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15, "reasoning_tokens": 2},
    }
    client = StubAsyncOpenAIClient(responses_payload=payload, embeddings_payload=[])
    service = OpenAIService(client=client, default_model="gpt-4", embedding_model="text-embedding-3-large")

    result = await service.generate_text("Tell me a joke")

    assert result == {
        "content": "hello world",
        "model": "gpt-4",
        "usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15, "reasoning_tokens": 2},
    }
    assert client.responses.calls[0]["model"] == "gpt-4"


@pytest.mark.asyncio
async def test_generate_text_supports_stream_like_payload_structure() -> None:
    payload = {
        "output": [
            {
                "content": [
                    {"type": "output_text", "text": "part one"},
                    {"type": "text", "text": " part two"},
                ]
            }
        ],
        "usage": {"input_tokens": 3},
    }
    client = StubAsyncOpenAIClient(responses_payload=payload, embeddings_payload=[])
    service = OpenAIService(client=client, default_model="gpt-4", embedding_model="text-embedding-3-large")

    result = await service.generate_text("Story time", model="gpt-4.1-mini")

    assert result["content"] == "part one part two"
    assert result["model"] == "gpt-4.1-mini"
    assert result["usage"] == {"input_tokens": 3}
    assert client.responses.calls[0]["model"] == "gpt-4.1-mini"


@pytest.mark.asyncio
async def test_generate_text_rejects_empty_prompt() -> None:
    client = StubAsyncOpenAIClient(responses_payload={}, embeddings_payload=[])
    service = OpenAIService(client=client, default_model="gpt-4", embedding_model="text-embedding-3-large")

    with pytest.raises(ValueError):
        await service.generate_text("   ")


@pytest.mark.asyncio
async def test_generate_text_raises_when_text_missing() -> None:
    payload: Dict[str, Any] = {"usage": {"input_tokens": 1}}
    client = StubAsyncOpenAIClient(responses_payload=payload, embeddings_payload=[])
    service = OpenAIService(client=client, default_model="gpt-4", embedding_model="text-embedding-3-large")

    with pytest.raises(RuntimeError):
        await service.generate_text("Prompt")


@pytest.mark.asyncio
async def test_create_embeddings_returns_vectors_and_usage() -> None:
    items = [StubEmbeddingItem([0.1, 0.2, 0.3]), StubEmbeddingItem([0.4, 0.5, 0.6])]
    usage = {"input_tokens": 6, "output_tokens": 0, "total_tokens": 6}
    client = StubAsyncOpenAIClient(responses_payload={}, embeddings_payload=items, usage=usage)
    service = OpenAIService(client=client, default_model="gpt-4", embedding_model="text-embedding-3-large")

    result = await service.create_embeddings(["alpha", "beta"], model="text-embedding-test")

    assert result == {
        "embeddings": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
        "model": "text-embedding-test",
        "usage": usage,
    }
    assert client.embeddings.calls[0]["model"] == "text-embedding-test"


@pytest.mark.asyncio
async def test_create_embeddings_uses_default_model_and_validates_input() -> None:
    client = StubAsyncOpenAIClient(responses_payload={}, embeddings_payload=[StubEmbeddingItem([0.9, 0.1])])
    service = OpenAIService(client=client, default_model="gpt-4", embedding_model="text-embedding-3-small")

    with pytest.raises(ValueError):
        await service.create_embeddings([])

    result = await service.create_embeddings(["hello"])
    assert result["model"] == "text-embedding-3-small"


@pytest.mark.asyncio
async def test_create_embeddings_raises_if_counts_mismatch() -> None:
    items = [StubEmbeddingItem([0.1, 0.2])]
    client = StubAsyncOpenAIClient(responses_payload={}, embeddings_payload=items)
    service = OpenAIService(client=client, default_model="gpt-4", embedding_model="text-embedding-3-small")

    with pytest.raises(RuntimeError):
        await service.create_embeddings(["a", "b"])

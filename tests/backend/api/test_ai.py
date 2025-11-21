from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Dict, List, Optional
from fastapi.testclient import TestClient
from openai import OpenAIError

from app.api import deps
from app.main import create_app


class StubOpenAIService:
    def __init__(self, *, text_response: Optional[Dict[str, Any]] = None, embeddings: Optional[Dict[str, Any]] = None):
        self._text_response = text_response or {
            "content": "stubbed response",
            "model": "gpt-5.1",
            "usage": {"input_tokens": 5, "output_tokens": 7, "total_tokens": 12},
        }
        self._embeddings = embeddings or {
            "embeddings": [[0.1, 0.2, 0.3]],
            "model": "text-embedding-3-large",
            "usage": {"input_tokens": 3, "output_tokens": 0, "total_tokens": 3},
        }

    async def generate_text(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_output_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        del prompt, model, temperature, max_output_tokens
        return self._text_response

    async def create_embeddings(self, texts: List[str], *, model: Optional[str] = None) -> Dict[str, Any]:
        del texts, model
        return self._embeddings


class RaisingOpenAIService(StubOpenAIService):
    def __init__(self, *, exc: Exception):
        super().__init__()
        self._exc = exc

    async def generate_text(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_output_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        del prompt, model, temperature, max_output_tokens
        raise self._exc

    async def create_embeddings(self, texts: List[str], *, model: Optional[str] = None) -> Dict[str, Any]:
        del texts, model
        raise self._exc


@contextmanager
def client_with_service(service: StubOpenAIService) -> TestClient:
    app = create_app()

    async def override_service():
        yield service

    app.dependency_overrides[deps.get_openai_service] = override_service
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(deps.get_openai_service, None)


def test_create_text_response_success() -> None:
    override_service = StubOpenAIService(
        text_response={"content": "hello", "model": "custom", "usage": {"input_tokens": 1, "output_tokens": 2}}
    )

    with client_with_service(override_service) as client:
        response = client.post(
            "/api/v1/ai/responses",
            json={"prompt": "Hi", "model": "custom", "temperature": 0.3, "max_output_tokens": 100},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["content"] == "hello"
    assert payload["model"] == "custom"
    assert payload["usage"] == {"input_tokens": 1, "output_tokens": 2, "total_tokens": None, "reasoning_tokens": None}


def test_create_text_response_value_error_translates_to_422() -> None:
    override_service = RaisingOpenAIService(exc=ValueError("bad prompt"))

    with client_with_service(override_service) as client:
        response = client.post("/api/v1/ai/responses", json={"prompt": "Hi"})

    assert response.status_code == 422
    assert response.json()["detail"] == "bad prompt"


def test_create_text_response_runtime_error_translates_to_502() -> None:
    override_service = RaisingOpenAIService(exc=RuntimeError("openai failure"))

    with client_with_service(override_service) as client:
        response = client.post("/api/v1/ai/responses", json={"prompt": "Hi"})

    assert response.status_code == 502
    assert response.json()["detail"] == "openai failure"


def test_create_text_response_openai_error_translates_to_generic_502() -> None:
    override_service = RaisingOpenAIService(exc=OpenAIError("api error"))

    with client_with_service(override_service) as client:
        response = client.post("/api/v1/ai/responses", json={"prompt": "Hi"})

    assert response.status_code == 502
    assert response.json()["detail"] == "OpenAI request failed."


def test_create_embeddings_success() -> None:
    override_service = StubOpenAIService(
        embeddings={
            "embeddings": [[0.9, 0.1]],
            "model": "custom-embed",
            "usage": {"input_tokens": 2, "output_tokens": 0, "total_tokens": 2},
        }
    )

    with client_with_service(override_service) as client:
        response = client.post("/api/v1/ai/embeddings", json={"texts": ["alpha", "beta"]})

    assert response.status_code == 200
    payload = response.json()
    assert payload["model"] == "custom-embed"
    assert payload["embeddings"] == [[0.9, 0.1]]
    assert payload["usage"] == {"input_tokens": 2, "output_tokens": 0, "total_tokens": 2, "reasoning_tokens": None}


def test_create_embeddings_value_error_translates_to_422() -> None:
    override_service = RaisingOpenAIService(exc=ValueError("invalid texts"))

    with client_with_service(override_service) as client:
        response = client.post("/api/v1/ai/embeddings", json={"texts": ["hello"]})

    assert response.status_code == 422
    assert response.json()["detail"] == "invalid texts"


def test_create_embeddings_runtime_error_translates_to_502() -> None:
    override_service = RaisingOpenAIService(exc=RuntimeError("downstream error"))

    with client_with_service(override_service) as client:
        response = client.post("/api/v1/ai/embeddings", json={"texts": ["hello"]})

    assert response.status_code == 502
    assert response.json()["detail"] == "downstream error"


def test_prompt_validation_error_triggers_422_before_service_call() -> None:
    # Pydantic validation should reject empty prompts before hitting the service.
    with client_with_service(StubOpenAIService()) as client:
        response = client.post("/api/v1/ai/responses", json={"prompt": ""})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "prompt"]


def test_embeddings_validation_error_triggers_422_before_service_call() -> None:
    with client_with_service(StubOpenAIService()) as client:
        response = client.post("/api/v1/ai/embeddings", json={"texts": []})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "texts"]

from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
if BACKEND_DIR.is_dir():
    backend_path = str(BACKEND_DIR)
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)

DEFAULT_ENV = {
    "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/testdb",
    "REDIS_URL": "redis://localhost:6379/0",
    "CELERY_BROKER_URL": "redis://localhost:6379/1",
    "CELERY_RESULT_BACKEND": "redis://localhost:6379/2",
    "JWT_SECRET": "test-secret",
    "OPENAI_API_KEY": "test-openai-key",
    "OPENAI_MODEL_NAME": "gpt-5.1",
    "OPENAI_EMBEDDING_MODEL": "text-embedding-3-large",
}

for key, value in DEFAULT_ENV.items():
    os.environ.setdefault(key, value)

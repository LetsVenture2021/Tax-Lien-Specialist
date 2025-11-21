#!/usr/bin/env bash
# Simple smoke test to ensure Alembic migrations can downgrade and upgrade cleanly.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"

cd "$BACKEND_DIR"

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL must be set for the migration smoke test." >&2
  exit 1
fi

export PYTHONPATH="${PYTHONPATH:-.}"

poetry run alembic upgrade head
poetry run alembic downgrade -1
poetry run alembic upgrade head

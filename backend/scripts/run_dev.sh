#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [ ! -d "${BACKEND_DIR}/.venv" ]; then
  echo "Missing venv at ${BACKEND_DIR}/.venv. Create it first."
  exit 1
fi

source "${BACKEND_DIR}/.venv/bin/activate"

if [ -f "${BACKEND_DIR}/.env" ]; then
  set -a
  source "${BACKEND_DIR}/.env"
  set +a
fi

if [ -z "${DATABASE_URL:-}" ]; then
  if [ -n "${PGHOST:-}" ] && [ -n "${PGUSER:-}" ] && [ -n "${PGPORT:-}" ] && [ -n "${PGDATABASE:-}" ]; then
    ENCODED_USER="${PGUSER//@/%40}"
    DATABASE_URL="postgresql+psycopg2://${ENCODED_USER}@${PGHOST}:${PGPORT}/${PGDATABASE}?sslmode=require"
    export DATABASE_URL
  else
    echo "DATABASE_URL is not set. Add it to ${BACKEND_DIR}/.env or set PGHOST/PGUSER/PGPORT/PGDATABASE."
    exit 1
  fi
fi

if ! command -v az >/dev/null 2>&1; then
  echo "Azure CLI not found. Install it or set PGPASSWORD manually."
  exit 1
fi

export PGPASSWORD="$(az account get-access-token \
  --resource https://ossrdbms-aad.database.windows.net \
  --query accessToken \
  --output tsv)"

cd "${BACKEND_DIR}"
exec uvicorn main:app --reload

#!/usr/bin/env bash

set -euo pipefail

DB_NAME="${DB_NAME:-reefsync}"
DB_USER="${DB_USER:-postgres}"

createdb -U "$DB_USER" "$DB_NAME" 2>/dev/null || true
psql -U "$DB_USER" -d "$DB_NAME" -f "$(dirname "$0")/schema.sql"
psql -U "$DB_USER" -d "$DB_NAME" -f "$(dirname "$0")/seed.sql"

# ReefSync DB bootstrap

This directory contains the PostgreSQL + PostGIS assets for the ReefSync data layer.

## Recommended setup

Use Docker Compose. This creates a local `reefsync` database automatically and applies the schema and seed files on first startup.

From the repo root:

```bash
docker compose up -d reefsync-db
```

Connection details:
- host: `localhost`
- port: `5432`
- database: `reefsync`
- user: `postgres`
- password: `postgres`

If the volume already exists and you need to re-run initialization from scratch:

```bash
docker compose down -v
docker compose up -d reefsync-db
```

## Native setup

Prerequisites:
- PostgreSQL 15+ with the PostGIS extension installed
- `createdb` and `psql` available in your shell

Run:

```bash
chmod +x backend/db/bootstrap_local.sh
./backend/db/bootstrap_local.sh
```

## Files

- [`docker-compose.yml`](/Users/PeterTenholder/SMathHacks2026/docker-compose.yml): PostGIS container that initializes `reefsync`
- [`schema.sql`](/Users/PeterTenholder/SMathHacks2026/backend/db/schema.sql): PostGIS schema, indexes, trigger, and coverage materialized view
- [`seed.sql`](/Users/PeterTenholder/SMathHacks2026/backend/db/seed.sql): Florida Keys seed data for orgs, users, zones, surveys, and diver assignments
- [`queries.py`](/Users/PeterTenholder/SMathHacks2026/backend/db/queries.py): raw SQL functions for Person 2 to import directly

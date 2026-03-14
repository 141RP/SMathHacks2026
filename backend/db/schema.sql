-- ReefSync schema for PostgreSQL + PostGIS.
-- Apply after creating the `reefsync` database.

CREATE EXTENSION IF NOT EXISTS postgis;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'survey_status') THEN
        CREATE TYPE survey_status AS ENUM ('planned', 'completed', 'cancelled');
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS orgs (
    id BIGSERIAL PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    contact_email TEXT,
    contact_phone TEXT,
    home_base GEOGRAPHY(POINT, 4326),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    org_id BIGINT NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL,
    cert_level TEXT,
    phone TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reef_zones (
    id BIGSERIAL PRIMARY KEY,
    org_id BIGINT REFERENCES orgs(id) ON DELETE SET NULL,
    zone_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    habitat_type TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    target_interval_days INTEGER NOT NULL DEFAULT 30 CHECK (target_interval_days > 0),
    notes TEXT,
    geom GEOMETRY(MULTIPOLYGON, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS surveys (
    id BIGSERIAL PRIMARY KEY,
    org_id BIGINT NOT NULL REFERENCES orgs(id) ON DELETE CASCADE,
    zone_id BIGINT REFERENCES reef_zones(id) ON DELETE SET NULL,
    lead_user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    survey_code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    survey_type TEXT NOT NULL,
    status survey_status NOT NULL,
    priority INTEGER NOT NULL DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    scheduled_start TIMESTAMPTZ NOT NULL,
    scheduled_end TIMESTAMPTZ NOT NULL,
    observed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    visibility_m NUMERIC(5, 2),
    max_depth_m NUMERIC(5, 2),
    notes TEXT,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT surveys_schedule_order_chk CHECK (scheduled_end >= scheduled_start)
);

CREATE TABLE IF NOT EXISTS survey_divers (
    survey_id BIGINT NOT NULL REFERENCES surveys(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assignment_role TEXT NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (survey_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_orgs_home_base_gist
    ON orgs USING GIST (home_base);

CREATE INDEX IF NOT EXISTS idx_reef_zones_geom_gist
    ON reef_zones USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_surveys_location_gist
    ON surveys USING GIST (location);

CREATE INDEX IF NOT EXISTS idx_surveys_status_start
    ON surveys (status, scheduled_start);

CREATE INDEX IF NOT EXISTS idx_surveys_zone_observed
    ON surveys (zone_id, observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_survey_divers_user
    ON survey_divers (user_id);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_surveys_set_updated_at ON surveys;

CREATE TRIGGER trg_surveys_set_updated_at
BEFORE UPDATE ON surveys
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP MATERIALIZED VIEW IF EXISTS zone_coverage_scores;

CREATE MATERIALIZED VIEW zone_coverage_scores AS
WITH latest_completed AS (
    SELECT
        s.zone_id,
        MAX(COALESCE(s.observed_at, s.completed_at, s.scheduled_end)) AS last_survey_at
    FROM surveys s
    WHERE s.status = 'completed'
      AND s.zone_id IS NOT NULL
    GROUP BY s.zone_id
)
SELECT
    z.id AS zone_id,
    z.zone_code,
    z.name AS zone_name,
    z.priority,
    z.target_interval_days,
    lc.last_survey_at,
    COALESCE(
        GREATEST(
            0,
            LEAST(
                100,
                ROUND(
                    (
                        1 - (
                            EXTRACT(EPOCH FROM (NOW() - lc.last_survey_at))
                            / 86400.0
                        ) / z.target_interval_days
                    ) * 100
                )
            )
        ),
        0
    )::INTEGER AS recency_score
FROM reef_zones z
LEFT JOIN latest_completed lc
    ON lc.zone_id = z.id;

CREATE UNIQUE INDEX IF NOT EXISTS idx_zone_coverage_scores_zone_id
    ON zone_coverage_scores (zone_id);

"""Raw SQL exports for ReefSync's data layer.

These functions intentionally return plain SQL strings so the API layer can
execute them with its own connection/session management.
"""


def get_surveys_map_feature_collection_sql() -> str:
    """Return all surveys as a GeoJSON FeatureCollection for map rendering."""
    return """
    SELECT jsonb_build_object(
        'type', 'FeatureCollection',
        'features', COALESCE(jsonb_agg(feature ORDER BY scheduled_start), '[]'::jsonb)
    ) AS feature_collection
    FROM (
        SELECT jsonb_build_object(
            'type', 'Feature',
            'geometry', ST_AsGeoJSON(s.location::geometry)::jsonb,
            'properties', jsonb_build_object(
                'id', s.id,
                'survey_code', s.survey_code,
                'title', s.title,
                'survey_type', s.survey_type,
                'status', s.status,
                'priority', s.priority,
                'scheduled_start', s.scheduled_start,
                'scheduled_end', s.scheduled_end,
                'observed_at', s.observed_at,
                'completed_at', s.completed_at,
                'org', jsonb_build_object(
                    'id', o.id,
                    'slug', o.slug,
                    'name', o.name
                ),
                'zone', CASE
                    WHEN z.id IS NULL THEN NULL
                    ELSE jsonb_build_object(
                        'id', z.id,
                        'zone_code', z.zone_code,
                        'name', z.name,
                        'priority', z.priority
                    )
                END,
                'lead_user', CASE
                    WHEN u.id IS NULL THEN NULL
                    ELSE jsonb_build_object(
                        'id', u.id,
                        'full_name', u.full_name,
                        'role', u.role
                    )
                END
            )
        ) AS feature,
        s.scheduled_start
        FROM surveys s
        JOIN orgs o
            ON o.id = s.org_id
        LEFT JOIN reef_zones z
            ON z.id = s.zone_id
        LEFT JOIN users u
            ON u.id = s.lead_user_id
    ) survey_features;
    """


def get_coverage_gaps_sql() -> str:
    """Return reef zones with no completed survey in the last %(lookback_days)s days."""
    return """
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
        z.id,
        z.zone_code,
        z.name,
        z.habitat_type,
        z.priority,
        z.target_interval_days,
        lc.last_survey_at,
        COALESCE(
            ROUND(EXTRACT(EPOCH FROM (NOW() - lc.last_survey_at)) / 86400.0),
            NULL
        ) AS days_since_last_survey,
        ST_AsGeoJSON(z.geom)::jsonb AS zone_geojson
    FROM reef_zones z
    LEFT JOIN latest_completed lc
        ON lc.zone_id = z.id
    WHERE lc.last_survey_at IS NULL
       OR lc.last_survey_at < NOW() - (%(lookback_days)s * INTERVAL '1 day')
    ORDER BY
        z.priority DESC,
        lc.last_survey_at NULLS FIRST,
        z.zone_code;
    """


def get_survey_overlaps_sql() -> str:
    """Return conflicting planned survey pairs within %(radius_meters)s meters and %(window_days)s days."""
    return """
    SELECT
        s1.id AS survey_a_id,
        s1.survey_code AS survey_a_code,
        s1.title AS survey_a_title,
        s1.scheduled_start AS survey_a_start,
        s1.scheduled_end AS survey_a_end,
        o1.name AS survey_a_org,
        s2.id AS survey_b_id,
        s2.survey_code AS survey_b_code,
        s2.title AS survey_b_title,
        s2.scheduled_start AS survey_b_start,
        s2.scheduled_end AS survey_b_end,
        o2.name AS survey_b_org,
        ROUND(ST_Distance(s1.location, s2.location))::INTEGER AS distance_meters,
        ROUND(
            ABS(EXTRACT(EPOCH FROM (s1.scheduled_start - s2.scheduled_start))) / 86400.0,
            2
        ) AS start_delta_days
    FROM surveys s1
    JOIN surveys s2
        ON s1.id < s2.id
       AND s1.status = 'planned'
       AND s2.status = 'planned'
       AND ABS(EXTRACT(EPOCH FROM (s1.scheduled_start - s2.scheduled_start))) <= (%(window_days)s * 86400)
       AND ST_DWithin(s1.location, s2.location, %(radius_meters)s)
    JOIN orgs o1
        ON o1.id = s1.org_id
    JOIN orgs o2
        ON o2.id = s2.org_id
    ORDER BY
        distance_meters ASC,
        LEAST(s1.scheduled_start, s2.scheduled_start) ASC;
    """


def get_survey_detail_sql() -> str:
    """Return one survey with org, zone, lead user, and diver roster as nested JSON."""
    return """
    SELECT jsonb_build_object(
        'id', s.id,
        'survey_code', s.survey_code,
        'title', s.title,
        'survey_type', s.survey_type,
        'status', s.status,
        'priority', s.priority,
        'scheduled_start', s.scheduled_start,
        'scheduled_end', s.scheduled_end,
        'observed_at', s.observed_at,
        'completed_at', s.completed_at,
        'visibility_m', s.visibility_m,
        'max_depth_m', s.max_depth_m,
        'notes', s.notes,
        'metadata', s.metadata,
        'location', ST_AsGeoJSON(s.location::geometry)::jsonb,
        'org', jsonb_build_object(
            'id', o.id,
            'slug', o.slug,
            'name', o.name,
            'contact_email', o.contact_email,
            'contact_phone', o.contact_phone
        ),
        'zone', CASE
            WHEN z.id IS NULL THEN NULL
            ELSE jsonb_build_object(
                'id', z.id,
                'zone_code', z.zone_code,
                'name', z.name,
                'habitat_type', z.habitat_type,
                'priority', z.priority,
                'target_interval_days', z.target_interval_days,
                'geometry', ST_AsGeoJSON(z.geom)::jsonb
            )
        END,
        'lead_user', CASE
            WHEN lead_user.id IS NULL THEN NULL
            ELSE jsonb_build_object(
                'id', lead_user.id,
                'full_name', lead_user.full_name,
                'email', lead_user.email,
                'role', lead_user.role,
                'cert_level', lead_user.cert_level
            )
        END,
        'diver_roster', COALESCE(roster.divers, '[]'::jsonb)
    ) AS survey
    FROM surveys s
    JOIN orgs o
        ON o.id = s.org_id
    LEFT JOIN reef_zones z
        ON z.id = s.zone_id
    LEFT JOIN users lead_user
        ON lead_user.id = s.lead_user_id
    LEFT JOIN LATERAL (
        SELECT jsonb_agg(
            jsonb_build_object(
                'user_id', u.id,
                'full_name', u.full_name,
                'email', u.email,
                'role', u.role,
                'cert_level', u.cert_level,
                'assignment_role', sd.assignment_role,
                'is_primary', sd.is_primary
            )
            ORDER BY sd.is_primary DESC, u.full_name ASC
        ) AS divers
        FROM survey_divers sd
        JOIN users u
            ON u.id = sd.user_id
        WHERE sd.survey_id = s.id
    ) roster ON TRUE
    WHERE s.id = %(survey_id)s;
    """


def refresh_zone_coverage_scores_sql() -> str:
    """Refresh the materialized view used for zone coverage scoring."""
    return "REFRESH MATERIALIZED VIEW zone_coverage_scores;"

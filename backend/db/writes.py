"""Write operations for ReefSync database."""

def insert_survey_sql() -> str:
    return """
    INSERT INTO surveys (org_id, location, scheduled_start, cert_level_required, max_capacity, status, title)
    VALUES ($1, ST_SetSRID(ST_Point($2, $3), 4326), $4, $5, $6, 'planned', $7)
    RETURNING id;
    """

def add_diver_to_survey_sql() -> str:
    return """
    INSERT INTO survey_divers (survey_id, user_id, assignment_role, is_primary)
    VALUES ($1, $2, 'diver', false)
    ON CONFLICT DO NOTHING;
    """

def check_survey_capacity_sql() -> str:
    return """
    SELECT 
        (SELECT COUNT(*) FROM survey_divers WHERE survey_id = $1) as current,
        max_capacity as max
    FROM surveys
    WHERE id = $1;
    """

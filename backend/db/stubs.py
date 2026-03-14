# STUB — replace with import from db/queries.py once Person 1 delivers

async def get_surveys_map():
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": { "type": "Point", "coordinates": [-80.1, 24.5] },
                "properties": {
                    "survey_id": 1,
                    "org_name": "ReefGuardians",
                    "planned_date": "2026-04-15",
                    "recency_score": 85,
                    "cert_required": "Advanced",
                    "capacity": 10,
                    "diver_count": 4,
                    "zone_name": "Key Largo North"
                }
            }
        ]
    }

async def get_survey_detail(survey_id: int):
    if survey_id == 1:
        return {
            "survey_id": 1,
            "org": { "org_id": 1, "name": "ReefGuardians" },
            "location": { "lat": 24.5, "lng": -80.1, "zone_name": "Key Largo North" },
            "planned_date": "2026-04-15",
            "cert_required": "Advanced",
            "capacity": 10,
            "divers": [ { "user_id": 101, "display_name": "Alice" } ],
            "diver_count": 1,
            "last_surveyed": "2025-10-10"
        }
    return None

async def get_coverage_gaps(days: int):
    return [
        {
            "zone_id": "Z1",
            "zone_name": "Key Largo South",
            "last_surveyed": "2025-09-01",
            "gap_days": 195,
            "coordinates": { "lat": 24.4, "lng": -80.2 }
        }
    ]

async def get_survey_overlaps():
    return []

async def insert_survey(data: dict):
    return 2

async def add_diver_to_survey(survey_id: int, user_id: int):
    return [{"user_id": user_id, "display_name": "New Diver"}]

async def check_survey_capacity(survey_id: int):
    return {"current": 4, "max": 10}

from fastapi import APIRouter, Depends
from typing import List
from ..schemas.coverage import GapZoneResponse
from ..db import queries
from ..db.engine import get_db_conn
import asyncpg

router = APIRouter()

@router.get("/gaps", response_model=List[GapZoneResponse])
async def get_coverage_gaps(days: int = 90, conn: asyncpg.Connection = Depends(get_db_conn)):
    sql = queries.get_coverage_gaps_sql()
    rows = await conn.fetch(sql.replace("%(lookback_days)s", "$1"), days)
    
    return [GapZoneResponse(
        zone_id=str(r['id']),
        zone_name=r['name'],
        last_surveyed=str(r['last_survey_at']),
        gap_days=int(r['days_since_last_survey']) if r['days_since_last_survey'] else 0,
        coordinates={"lat": 0.0, "lng": 0.0} # Stub for extraction from GeoJSON
    ) for r in rows]

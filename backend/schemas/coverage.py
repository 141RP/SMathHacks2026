from pydantic import BaseModel
from typing import List

class GapZoneResponse(BaseModel):
    zone_id: str
    zone_name: str
    last_surveyed: str
    gap_days: int
    coordinates: dict # {lat: float, lng: float}

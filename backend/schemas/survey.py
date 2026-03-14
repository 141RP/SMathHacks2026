from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Location(BaseModel):
    lat: float
    lng: float
    zone_name: str

class OrgInfo(BaseModel):
    org_id: int
    name: str

class DiverShort(BaseModel):
    user_id: int
    display_name: str

class SurveyDetailResponse(BaseModel):
    survey_id: int
    org: OrgInfo
    location: Location
    planned_date: str
    cert_required: str
    capacity: int
    divers: List[DiverShort]
    diver_count: int
    last_surveyed: str
    ai_summary: Optional[str] = None

class SurveyCreateRequest(BaseModel):
    location: Location
    planned_date: str
    cert_required: str
    capacity: int

class OverlapItem(BaseModel):
    survey_id: int
    org_name: str
    planned_date: str
    location: str

class OverlapResponse(BaseModel):
    survey_a: OverlapItem
    survey_b: OverlapItem
    distance_km: float
    days_apart: int

# GeoJSON Models
class Geometry(BaseModel):
    type: str = "Point"
    coordinates: List[float] # [lng, lat]

class SurveyProperties(BaseModel):
    survey_id: int
    org_name: str
    planned_date: str
    recency_score: int
    cert_required: str
    capacity: int
    diver_count: int
    zone_name: str

class Feature(BaseModel):
    type: str = "Feature"
    geometry: Geometry
    properties: SurveyProperties

class SurveyMapResponse(BaseModel):
    type: str = "FeatureCollection"
    features: List[Feature]

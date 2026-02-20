from pydantic import BaseModel
from typing import List, Optional


class POIBlock(BaseModel):
    poi_id: str
    name: str
    category: str
    lat: float
    lon: float
    duration_minutes: int
    travel_minutes_from_previous: int
    indoor: bool
    source: Optional[str] = None


class DayPlan(BaseModel):
    day: int
    blocks: List[POIBlock]


class TripConstraints(BaseModel):
    days: int
    pace: str  # relaxed | moderate | packed
    daily_start_hour: int = 9
    daily_end_hour: int = 18


class TripState(BaseModel):
    city: str
    interests: List[str]
    constraints: TripConstraints
    days: List[DayPlan]
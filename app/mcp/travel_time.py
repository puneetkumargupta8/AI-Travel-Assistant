import math
from pydantic import BaseModel


class TravelTimeInput(BaseModel):
    lat1: float
    lon1: float
    lat2: float
    lon2: float


class TravelTimeOutput(BaseModel):
    distance_km: float
    estimated_travel_minutes: int


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def estimate_travel_time(input_data: TravelTimeInput) -> TravelTimeOutput:
    distance = haversine_distance(
        input_data.lat1,
        input_data.lon1,
        input_data.lat2,
        input_data.lon2
    )

    # Delhi city heuristic:
    # Average effective city speed ≈ 25 km/h
    avg_speed_kmh = 25

    travel_time_hours = distance / avg_speed_kmh
    travel_time_minutes = int(travel_time_hours * 60)

    # Add 10 minute buffer for traffic variability
    travel_time_minutes += 10

    return TravelTimeOutput(
        distance_km=round(distance, 2),
        estimated_travel_minutes=travel_time_minutes
    )
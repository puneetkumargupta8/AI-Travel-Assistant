from typing import List
from app.state import DayPlan, POIBlock, TripConstraints
from app.mcp.travel_time import estimate_travel_time, TravelTimeInput
from app.mcp.poi_search import POISearchOutput


PACE_LIMITS = {
    "relaxed": 3,
    "moderate": 4,
    "packed": 5
}


def build_itinerary(
    pois: List[POISearchOutput],
    constraints: TripConstraints
) -> List[DayPlan]:

    days_output = []
    pois_per_day = PACE_LIMITS.get(constraints.pace, 3)

    available_minutes = (constraints.daily_end_hour - constraints.daily_start_hour) * 60

    poi_index = 0

    for day_number in range(1, constraints.days + 1):

        day_blocks = []
        total_time = 0
        last_poi = None
        count = 0

        while (
            poi_index < len(pois)
            and count < pois_per_day
        ):
            poi = pois[poi_index]

            travel_minutes = 0

            if last_poi:
                travel = estimate_travel_time(
                    TravelTimeInput(
                        lat1=last_poi.lat,
                        lon1=last_poi.lon,
                        lat2=poi.lat,
                        lon2=poi.lon
                    )
                )
                travel_minutes = travel.estimated_travel_minutes

            projected_time = total_time + travel_minutes + poi.suggested_duration

            if projected_time > available_minutes:
                break

            block = POIBlock(
                poi_id=poi.poi_id,
                name=poi.name,
                category=poi.category,
                lat=poi.lat,
                lon=poi.lon,
                duration_minutes=poi.suggested_duration,
                travel_minutes_from_previous=travel_minutes,
                indoor=poi.indoor,
                source=poi.source
            )

            day_blocks.append(block)

            total_time = projected_time
            last_poi = poi
            poi_index += 1
            count += 1

        days_output.append(
            DayPlan(
                day=day_number,
                blocks=day_blocks
            )
        )

    return days_output
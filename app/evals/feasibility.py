from app.state import TripState
from app.mcp.itinerary_builder import PACE_LIMITS
from typing import Dict, Any


def evaluate_feasibility(trip: TripState) -> Dict[str, Any]:

    results = []
    overall_status = "PASS"

    available_minutes = (
        trip.constraints.daily_end_hour - trip.constraints.daily_start_hour
    ) * 60

    for day in trip.days:

        total_time = 0
        travel_issues = []
        pace_limit = PACE_LIMITS.get(trip.constraints.pace, 3)

        for block in day.blocks:
            total_time += block.duration_minutes
            total_time += block.travel_minutes_from_previous

            if block.travel_minutes_from_previous > 90:
                travel_issues.append({
                    "poi": block.name,
                    "travel_minutes": block.travel_minutes_from_previous
                })

        day_status = "PASS"

        if total_time > available_minutes:
            day_status = "FAIL"
            overall_status = "FAIL"

        if len(day.blocks) > pace_limit:
            day_status = "FAIL"
            overall_status = "FAIL"

        if travel_issues:
            day_status = "FAIL"
            overall_status = "FAIL"

        results.append({
            "day": day.day,
            "total_minutes": total_time,
            "available_minutes": available_minutes,
            "poi_count": len(day.blocks),
            "pace_limit": pace_limit,
            "travel_issues": travel_issues,
            "status": day_status
        })

    return {
        "overall_status": overall_status,
        "day_results": results
    }
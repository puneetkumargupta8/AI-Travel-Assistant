from app.state import TripState
from typing import Dict, Any


def evaluate_grounding(trip: TripState) -> Dict[str, Any]:

    issues = []
    total_blocks = 0

    for day in trip.days:
        if not day.blocks:
            issues.append({
                "day": day.day,
                "issue": "No POIs planned for this day."
            })

        for block in day.blocks:
            total_blocks += 1

            if not block.poi_id.startswith("osm_"):
                issues.append({
                    "poi": block.name,
                    "issue": "Invalid POI ID format"
                })

            if block.lat is None or block.lon is None:
                issues.append({
                    "poi": block.name,
                    "issue": "Missing coordinates"
                })

            if block.source != "OpenStreetMap":
                issues.append({
                    "poi": block.name,
                    "issue": "Missing or invalid source attribution"
                })

    status = "PASS" if not issues else "FAIL"

    return {
        "total_pois_checked": total_blocks,
        "issues_found": issues,
        "overall_status": status
    }
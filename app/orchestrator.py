from app.state import TripState, TripConstraints
from app.mcp.poi_search import search_pois, POISearchInput
from app.mcp.itinerary_builder import build_itinerary
from app.mcp.weather_adjustment import adjust_for_weather


class Orchestrator:

    def __init__(self):
        self.current_trip: TripState | None = None

    def plan_trip(self, city: str, interests: list[str], days: int, pace: str):

        poi_input = POISearchInput(
            city=city,
            interests=interests,
            max_results=25
        )

        pois = search_pois(poi_input)

        constraints = TripConstraints(
            days=days,
            pace=pace
        )

        itinerary_days = build_itinerary(pois, constraints)

        self.current_trip = TripState(
            city=city,
            interests=interests,
            constraints=constraints,
            days=itinerary_days
        )

        return self.current_trip

    def edit_day_pace(self, day_number: int, new_pace: str):

        if not self.current_trip:
            raise ValueError("No active trip to edit.")

        if day_number < 1 or day_number > len(self.current_trip.days):
            raise ValueError("Invalid day number.")

        # Extract all original POIs used in that day
        original_day = self.current_trip.days[day_number - 1]

        # Re-search POIs using same city and interests
        poi_input = POISearchInput(
            city=self.current_trip.city,
            interests=self.current_trip.interests,
            max_results=25
        )

        pois = search_pois(poi_input)

        # Build new itinerary for one day only
        constraints = TripConstraints(
            days=1,
            pace=new_pace,
            daily_start_hour=self.current_trip.constraints.daily_start_hour,
            daily_end_hour=self.current_trip.constraints.daily_end_hour
        )

        rebuilt_day = build_itinerary(pois, constraints)[0]

        # Replace only that day
        self.current_trip.days[day_number - 1] = rebuilt_day

        return self.current_trip

    def explain(self, target: str | None = None):

        if not self.current_trip:
            return {"error": "No active trip to explain."}

        # If target is None or "plan", explain overall structure
        if not target or target.lower() == "plan":
            total_pois = sum(len(day.blocks) for day in self.current_trip.days)

            return {
                "type": "PLAN_EXPLANATION",
                "message": f"This itinerary covers {total_pois} places across {self.current_trip.constraints.days} days at a {self.current_trip.constraints.pace} pace. Travel times were estimated using city distance heuristics and daily time windows were respected."
            }

        # Otherwise explain specific POI
        for day in self.current_trip.days:
            for block in day.blocks:
                if target.lower() in block.name.lower():

                    interest_match = any(
                        interest.lower() in block.category.lower()
                        for interest in self.current_trip.interests
                    )

                    return {
                        "type": "POI_EXPLANATION",
                        "poi": block.name,
                        "message": f"{block.name} was selected because it aligns with your interests ({', '.join(self.current_trip.interests)}). It fits within the daily time window and maintains travel efficiency."
                    }

        return {"error": "Target not found in itinerary."}

    def apply_weather_adjustment(self):

        if not self.current_trip:
            return {"error": "No active trip"}

        self.current_trip = adjust_for_weather(self.current_trip)

        return self.current_trip
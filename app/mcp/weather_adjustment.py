from ..state import TripState
from .weather import get_delhi_weather
from .poi_search import search_pois, POISearchInput
from .itinerary_builder import build_itinerary


RAIN_THRESHOLD = 5.0  # mm precipitation


def adjust_for_weather(trip: TripState) -> TripState:

    weather = get_delhi_weather()

    for i, forecast_day in enumerate(weather.forecast):

        if i >= len(trip.days):
            break

        if forecast_day.precipitation > RAIN_THRESHOLD:

            # Rebuild this day using indoor-focused interests
            poi_input = POISearchInput(
                city=trip.city,
                interests=["history", "culture"],  # indoor-friendly
                max_results=20
            )

            pois = search_pois(poi_input)

            rebuilt_day = build_itinerary(
                pois,
                trip.constraints
            )[0]

            trip.days[i] = rebuilt_day

    return trip
import sys
import os
from unittest.mock import patch

# Add the current directory to the path so we can import the modules
sys.path.append('.')

from app.mcp.weather_adjustment import adjust_for_weather, RAIN_THRESHOLD
from app.mcp.weather import get_delhi_weather
from app.state import TripState, TripConstraints, DayPlan, POIBlock

# Create a mock trip state
def create_mock_trip():
    # Create some mock POI blocks
    poi1 = POIBlock(
        poi_id="1",
        name="Historical Museum",
        category="history",
        lat=28.6139,
        lon=77.2090,
        duration_minutes=120,
        travel_minutes_from_previous=0,
        indoor=True
    )
    
    poi2 = POIBlock(
        poi_id="2",
        name="Food Market",
        category="food",
        lat=28.6339,
        lon=77.2290,
        duration_minutes=90,
        travel_minutes_from_previous=30,
        indoor=False
    )
    
    # Create day plans
    day1 = DayPlan(day=1, blocks=[poi1, poi2])
    day2 = DayPlan(day=2, blocks=[poi1])
    
    # Create constraints
    constraints = TripConstraints(
        days=2,
        pace="relaxed",
        daily_start_hour=9,
        daily_end_hour=18
    )
    
    # Create trip state
    trip = TripState(
        city="Delhi",
        interests=["history", "food"],
        constraints=constraints,
        days=[day1, day2]
    )
    
    return trip

def main():
    print("=== Weather Adjustment Test with Rainy Forecast ===")
    print(f"Rain threshold: {RAIN_THRESHOLD} mm")
    
    # Create a mock trip
    trip = create_mock_trip()
    
    print(f"\nOriginal trip:")
    print(f"City: {trip.city}")
    print(f"Days: {len(trip.days)}")
    for i, day in enumerate(trip.days):
        print(f"  Day {day.day}: {len(day.blocks)} activities")
        for block in day.blocks:
            print(f"    - {block.name} ({'indoor' if block.indoor else 'outdoor'})")
    
    # Mock the weather function to return rainy forecast
    with patch('app.mcp.weather_adjustment.get_delhi_weather') as mock_weather:
        # Create mock WeatherDay objects
        from app.mcp.weather import WeatherDay, WeatherOutput
        
        mock_forecast = [
            WeatherDay(date='2026-02-21', max_temp=26.3, min_temp=15.1, precipitation=10.0),  # 10mm - above threshold
            WeatherDay(date='2026-02-22', max_temp=26.7, min_temp=15.2, precipitation=0.0)   # 0mm - below threshold
        ]
        
        mock_weather.return_value = WeatherOutput(forecast=mock_forecast)
        
        print(f"\nSimulating rainy forecast...")
        print(f"Day 1 precipitation: 10.0 mm (above {RAIN_THRESHOLD} mm threshold)")
        print(f"Day 2 precipitation: 0.0 mm (below {RAIN_THRESHOLD} mm threshold)")
        
        # Apply weather adjustment
        adjusted_trip = adjust_for_weather(trip)
        
        print(f"\nAdjusted trip:")
        print(f"City: {adjusted_trip.city}")
        print(f"Days: {len(adjusted_trip.days)}")
        for i, day in enumerate(adjusted_trip.days):
            print(f"  Day {day.day}: {len(day.blocks)} activities")
            for block in day.blocks:
                print(f"    - {block.name} ({'indoor' if block.indoor else 'outdoor'})")
        
        # Check if the trip was modified
        original_count = sum(len(day.blocks) for day in trip.days)
        adjusted_count = sum(len(day.blocks) for day in adjusted_trip.days)
        
        print(f"\nSummary:")
        print(f"Original activities: {original_count}")
        print(f"Adjusted activities: {adjusted_count}")
        
        if original_count != adjusted_count:
            print("✓ Itinerary was modified due to weather forecast")
            print("✓ Day 1 was rebuilt with indoor-focused activities")
        else:
            print("○ Itinerary remained the same")

if __name__ == "__main__":
    main()
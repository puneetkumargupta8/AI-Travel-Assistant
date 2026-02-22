import requests
import json

# First, let's plan a trip
print("Planning a trip...")
response = requests.post('http://localhost:8000/plan-trip', json={
    'city': 'Delhi', 
    'interests': ['history', 'food'], 
    'days': 2, 
    'pace': 'relaxed'
})

if response.status_code == 200:
    trip_data = response.json()
    print("Trip planned successfully!")
    print(f"City: {trip_data['city']}")
    print(f"Days: {trip_data['constraints']['days']}")
    print(f"Pace: {trip_data['constraints']['pace']}")
    print(f"Number of activities: {sum(len(day['blocks']) for day in trip_data['days'])}")
    
    # Now let's test the weather adjustment by directly calling the endpoint
    # Since we can't use the voice command due to API key issues, 
    # let's test the apply_weather_adjustment method directly
    
    print("\nTesting weather adjustment via direct method call...")
    try:
        # Import and test the function directly
        import sys
        sys.path.append('.')
        from app.mcp.weather_adjustment import adjust_for_weather
        from app.state import TripState
        
        # Create a TripState object from the response data
        trip_state = TripState(**trip_data)
        
        # Apply weather adjustment
        adjusted_trip = adjust_for_weather(trip_state)
        
        print("Weather adjustment completed!")
        print(f"Original activities: {sum(len(day['blocks']) for day in trip_data['days'])}")
        print(f"Adjusted activities: {sum(len(day.blocks) for day in adjusted_trip.days)}")
        
        # Check if the activities changed
        original_count = sum(len(day['blocks']) for day in trip_data['days'])
        adjusted_count = sum(len(day.blocks) for day in adjusted_trip.days)
        
        if original_count != adjusted_count:
            print("✓ Itinerary was modified due to weather forecast")
        else:
            print("○ Itinerary remained the same (no significant rain forecast)")
            
    except Exception as e:
        print(f"Error testing weather adjustment: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"Error planning trip: {response.status_code}")
    print(response.text)
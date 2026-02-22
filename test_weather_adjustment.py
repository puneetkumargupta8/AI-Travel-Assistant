import requests
import json

# Test planning a trip
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
    
    # Test the weather adjustment
    print("\nTesting weather adjustment...")
    voice_response = requests.post('http://localhost:8000/voice-command', json={
        'text': 'What if it rains?'
    })
    
    if voice_response.status_code == 200:
        voice_data = voice_response.json()
        print(f"Intent: {voice_data['intent']}")
        if voice_data['intent'] == 'WEATHER_ADJUSTMENT':
            updated_trip = voice_data['trip']
            print("Trip adjusted for weather!")
            print(f"Updated activities: {sum(len(day['blocks']) for day in updated_trip['days'])}")
        else:
            print("Weather adjustment not triggered")
            print(voice_data)
    else:
        print(f"Error in voice command: {voice_response.status_code}")
        print(voice_response.text)
else:
    print(f"Error planning trip: {response.status_code}")
    print(response.text)
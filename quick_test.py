import requests

# Quick manual tests
print("=== Quick Manual Tests ===")

# Test 1: Basic health check
response = requests.get("http://localhost:8000/")
print(f"1. Health check: {response.status_code == 200} - {response.json()}")

# Test 2: Plan trip
response = requests.post("http://localhost:8000/plan-trip", json={
    "city": "Delhi", 
    "interests": ["history"], 
    "days": 1, 
    "pace": "relaxed"
})
print(f"2. Plan trip: {response.status_code == 200}")
if response.status_code == 200:
    data = response.json()
    print(f"   City: {data['city']}, Days: {data['constraints']['days']}")

# Test 3: Voice command - PLAN
response = requests.post("http://localhost:8000/voice-command", json={
    "text": "Plan a trip to Mumbai"
})
print(f"3. Voice PLAN: {response.status_code == 200}")
if response.status_code == 200:
    data = response.json()
    print(f"   Intent: {data.get('intent')}")

# Test 4: Voice command - EXPLAIN
response = requests.post("http://localhost:8000/voice-command", json={
    "text": "Explain the plan"
})
print(f"4. Voice EXPLAIN: {response.status_code == 200}")
if response.status_code == 200:
    data = response.json()
    print(f"   Intent: {data.get('intent')}")

# Test 5: Weather
response = requests.get("http://localhost:8000/test-weather")
print(f"5. Weather: {response.status_code == 200}")
if response.status_code == 200:
    data = response.json()
    print(f"   Forecast days: {len(data.get('forecast', []))}")

# Test 6: Weather adjustment voice command
response = requests.post("http://localhost:8000/voice-command", json={
    "text": "What if it rains?"
})
print(f"6. Weather adjustment: {response.status_code == 200}")
if response.status_code == 200:
    data = response.json()
    print(f"   Intent: {data.get('intent')}")

print("\n=== All tests completed ===")
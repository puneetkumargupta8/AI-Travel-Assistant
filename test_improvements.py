from app.intents import classify_intent, clean_json_response
import json

print("=== Testing Intent Classification Improvements ===")

# Test 1: Clean JSON response function
print("\n1. Testing clean_json_response function:")
test_cases = [
    '```json\n{"intent": "PLAN"}\n```',
    '{"intent": "EDIT_DAY_PACE"}',
    '```{"intent": "EXPLAIN"}\n```',
    '  {"intent": "PLAN", "city": "Delhi"}  '
]

for i, test_text in enumerate(test_cases, 1):
    result = clean_json_response(test_text)
    print(f"  Test {i}: {repr(test_text)} -> {repr(result)}")

# Test 2: Test classify_intent with timeout
print("\n2. Testing classify_intent function:")
try:
    result = classify_intent("Plan a trip to Delhi")
    print(f"  Result: {result}")
    print("  ✓ Function completed successfully")
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\n=== All tests completed ===")
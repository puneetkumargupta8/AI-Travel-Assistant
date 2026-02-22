import requests
import time

def test_voice_command():
    try:
        print("Testing voice command with timeout...")
        start_time = time.time()
        response = requests.post(
            'http://localhost:8000/voice-command', 
            json={'text': 'Plan a trip to Delhi'}, 
            timeout=15
        )
        end_time = time.time()
        
        print(f"Status: {response.status_code}")
        print(f"Response time: {end_time - start_time:.2f} seconds")
        print(f"Response: {response.json()}")
        print("✓ Voice command test completed successfully!")
        
    except requests.exceptions.Timeout:
        print("✗ Request timed out")
    except Exception as e:
        print(f"✗ Error: {str(e)}")

if __name__ == "__main__":
    test_voice_command()
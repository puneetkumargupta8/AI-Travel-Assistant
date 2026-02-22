import streamlit as st
import requests
import os

# Test the Streamlit UI rendering
st.title("Streamlit UI Test")
st.write("Testing Evaluation Panel Implementation")

# Check if the required session state variables exist
required_vars = ['trip_data', 'evaluation_results']
missing_vars = [var for var in required_vars if var not in st.session_state]

if missing_vars:
    st.info(f"Missing session state variables: {missing_vars}")
else:
    st.success("All required session state variables are present")

# Test API connection
try:
    api_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    response = requests.get(f"{api_url}/")
    if response.status_code == 200:
        st.success("✅ Backend connection successful")
    else:
        st.warning(f"⚠️ Backend returned status: {response.status_code}")
except Exception as e:
    st.error(f"❌ Backend connection failed: {str(e)}")

st.divider()
st.write("The Evaluation Panel should appear below the itinerary when a trip is generated.")
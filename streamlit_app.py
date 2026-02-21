import streamlit as st
import requests
import json
from datetime import datetime
import os

# Set page config
st.set_page_config(
    page_title="AI Travel Assistant",
    page_icon="✈️",
    layout="wide"
)

# Title
st.title("✈️ AI Travel Assistant")
st.markdown("Plan your perfect trip with AI-powered recommendations")

# Voice Command Section
st.divider()
st.subheader("🎤 Voice Commands")
voice_input = st.text_input("Speak or type your request", placeholder="e.g., 'What if it rains?', 'Plan a trip to Delhi', 'Explain the itinerary'")
col1, col2 = st.columns(2)

with col1:
    if st.button("Submit Voice Command", type="primary"):
        if voice_input.strip():
            with st.spinner("Processing your request..."):
                try:
                    api_url = os.getenv("BACKEND_URL", "http://localhost:8000")
                    response = requests.post(f"{api_url}/voice-command", json={
                        "text": voice_input
                    })
                    
                    if response.status_code == 200:
                        voice_response = response.json()
                        st.session_state.last_response = voice_response
                        
                        intent = voice_response.get("intent")
                        if intent in ["PLAN", "EDIT_DAY_PACE", "WEATHER_ADJUSTMENT"]:
                            # Store the trip data
                            if "trip" in voice_response:
                                st.session_state.trip_data = voice_response["trip"]
                                st.success("Command processed successfully!")
                                st.rerun()
                        elif intent == "EXPLAIN":
                            st.session_state.last_explanation = voice_response.get("explanation", {})
                            st.success("Explanation generated!")
                        else:
                            st.info(f"Command processed with intent: {intent}")
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {str(e)}")
        else:
            st.warning("Please enter a command first.")

with col2:
    if st.button("Adjust for Weather"):
        if 'trip_data' in st.session_state:
            with st.spinner("Adjusting itinerary for weather..."):
                try:
                    # Simulate voice command for weather adjustment
                    api_url = os.getenv("BACKEND_URL", "http://localhost:8000")
                    response = requests.post(f"{api_url}/voice-command", json={
                        "text": "What if it rains?"
                    })
                    
                    if response.status_code == 200:
                        voice_response = response.json()
                        if voice_response.get("intent") == "WEATHER_ADJUSTMENT" and "trip" in voice_response:
                            st.session_state.trip_data = voice_response["trip"]
                            st.session_state.last_response = voice_response
                            st.success("Itinerary adjusted for weather conditions!")
                            st.rerun()
                        else:
                            st.info("No weather adjustment needed for current forecast.")
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {str(e)}")
        else:
            st.warning("Please generate a trip first before adjusting for weather.")

# Sidebar for inputs
with st.sidebar:
    st.header("Trip Configuration")
    
    city = st.text_input("City", "Delhi")
    interests = st.multiselect(
        "Interests",
        ["history", "food", "culture", "nature", "shopping", "architecture", "museums"],
        default=["history", "food"]
    )
    days = st.slider("Number of days", 1, 7, 2)
    pace = st.selectbox("Pace", ["relaxed", "moderate", "packed"], index=1)
    
    if st.button("Generate Itinerary"):
        if not interests:
            st.error("Please select at least one interest.")
        else:
            with st.spinner("Generating your personalized itinerary..."):
                try:
                    # Make API call to FastAPI backend
                    api_url = os.getenv("BACKEND_URL", "http://localhost:8000")
                    response = requests.post(f"{api_url}/plan-trip", json={
                        "city": city,
                        "interests": interests,
                        "days": days,
                        "pace": pace
                    })
                    
                    if response.status_code == 200:
                        trip_data = response.json()
                        st.session_state.trip_data = trip_data
                        st.success("Itinerary generated successfully!")
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {str(e)}")

# Display Explanations with Sources
if 'last_explanation' in st.session_state:
    st.divider()
    st.subheader("📝 Explanation")
    explanation = st.session_state.last_explanation
    exp_type = explanation.get("type", "GENERAL")
    
    st.info(f"**Type:** {exp_type}")
    st.write(explanation.get("message", "No explanation available."))
    
    # Show sources if available
    if explanation.get("sources"):
        with st.expander("🔍 Sources"):
            for source in explanation["sources"]:
                st.write(f"• {source}")

# Main content area
if 'trip_data' in st.session_state:
    trip = st.session_state.trip_data
    
    st.subheader(f"Your {trip['city']} Trip Itinerary")
    st.write(f"**Interests:** {', '.join(trip['interests'])}")
    st.write(f"**Duration:** {trip['constraints']['days']} days")
    st.write(f"**Pace:** {trip['constraints']['pace']}")
    
    # Display each day
    for day_plan in trip['days']:
        day_num = day_plan['day']
        st.divider()
        st.subheader(f"Day {day_num}")
        
        if 'blocks' in day_plan and day_plan['blocks']:
            for i, block in enumerate(day_plan['blocks']):
                with st.expander(f"📍 {block['name']} ({block['category']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Duration:** {block['duration_minutes']} minutes")
                        if block.get('travel_minutes_from_previous', 0) > 0:
                            st.write(f"**Travel time:** {block['travel_minutes_from_previous']} minutes")
                    
                    with col2:
                        st.write(f"**Location:** [{block['lat']:.4f}, {block['lon']:.4f}]")
                        if block.get('indoor'):
                            st.write("**Type:** Indoor")
                        else:
                            st.write("**Type:** Outdoor")
                        
                        if block.get('source'):
                            st.write(f"**Source:** {block['source']}")
        else:
            st.info("No activities planned for this day.")
else:
    st.info("Configure your trip in the sidebar and click 'Generate Itinerary' to get started.")

# Add section for editing day pace
if 'trip_data' in st.session_state:
    st.divider()
    st.subheader("Edit Day Pace")
    
    col1, col2 = st.columns(2)
    
    with col1:
        day_to_edit = st.number_input("Day to edit", min_value=1, max_value=len(st.session_state.trip_data['days']), value=1)
    
    with col2:
        new_pace = st.selectbox("New pace for this day", ["relaxed", "moderate", "packed"])
    
    if st.button("Update Day"):
        with st.spinner(f"Updating day {day_to_edit} pace..."):
            try:
                api_url = os.getenv("BACKEND_URL", "http://localhost:8000")
                response = requests.post(f"{api_url}/edit-day", json={
                    "day": int(day_to_edit),
                    "pace": new_pace
                })
                
                if response.status_code == 200:
                    updated_trip = response.json()['trip']
                    st.session_state.trip_data = updated_trip
                    st.success(f"Day {day_to_edit} updated successfully!")
                    st.rerun()
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {str(e)}")

# Add section for weather information
if 'trip_data' in st.session_state:
    st.divider()
    st.subheader("🌤️ Weather Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Get Weather Forecast"):
            with st.spinner("Fetching weather information..."):
                try:
                    api_url = os.getenv("BACKEND_URL", "http://localhost:8000")
                    response = requests.get(f"{api_url}/test-weather")
                    
                    if response.status_code == 200:
                        weather_data = response.json()
                        st.session_state.current_weather = weather_data
                        st.success("Weather data retrieved!")
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {str(e)}")
    
    with col2:
        if st.button("Adjust for Weather"):
            if 'trip_data' in st.session_state:
                with st.spinner("Adjusting itinerary for weather..."):
                    try:
                        # Simulate voice command for weather adjustment
                        api_url = os.getenv("BACKEND_URL", "http://localhost:8000")
                        response = requests.post(f"{api_url}/voice-command", json={
                            "text": "What if it rains?"
                        })
                        
                        if response.status_code == 200:
                            voice_response = response.json()
                            if voice_response.get("intent") == "WEATHER_ADJUSTMENT" and "trip" in voice_response:
                                st.session_state.trip_data = voice_response["trip"]
                                st.session_state.last_response = voice_response
                                st.success("Itinerary adjusted for weather conditions!")
                                st.rerun()
                            else:
                                st.info("No weather adjustment needed for current forecast.")
                        else:
                            st.error(f"Error: {response.status_code} - {response.text}")
                    except Exception as e:
                        st.error(f"Failed to connect to backend: {str(e)}")
            else:
                st.warning("Please generate a trip first.")

    # Display current weather if available
    if 'current_weather' in st.session_state:
        st.write("**Current Weather Forecast:**")
        weather = st.session_state.current_weather
        if 'forecast' in weather:
            for i, day_forecast in enumerate(weather['forecast'][:3]):  # Show first 3 days
                precip = day_forecast.get('precipitation', 0)
                status = "🌧️ Rainy" if precip > 5.0 else "☀️ Clear"
                st.write(f"Day {i+1} ({day_forecast.get('date', 'N/A')}): {status} - {precip}mm precipitation")

# Evaluation Panel
if 'trip_data' in st.session_state:
    st.divider()
    st.subheader("📊 Evaluation Panel")
    
    if st.button("Run Evaluations"):
        with st.spinner("Running evaluations..."):
            try:
                api_url = os.getenv("BACKEND_URL", "http://localhost:8000")
                
                # Run Feasibility Evaluation
                feas_response = requests.get(f"{api_url}/run-feasibility")
                feasibility_result = feas_response.json() if feas_response.status_code == 200 else {"error": "Failed to fetch"}
                
                # Run Grounding Evaluation
                ground_response = requests.get(f"{api_url}/run-grounding")
                grounding_result = ground_response.json() if ground_response.status_code == 200 else {"error": "Failed to fetch"}
                
                # Store results in session state
                st.session_state.evaluation_results = {
                    "feasibility": feasibility_result,
                    "grounding": grounding_result
                }
                
                st.success("Evaluations completed!")
                
            except Exception as e:
                st.error(f"Failed to run evaluations: {str(e)}")
    
    # Display evaluation results if available
    if 'evaluation_results' in st.session_state:
        results = st.session_state.evaluation_results
        
        st.subheader("Evaluation Results")
        
        # Feasibility Evaluation
        feas_result = results.get("feasibility", {})
        if "error" not in feas_result:
            st.markdown("### 📋 Feasibility Evaluation")
            overall_status = feas_result.get("overall_status", "Unknown")
            status_color = "🟢" if overall_status == "FEASIBLE" else "🔴" if overall_status == "INFEASIBLE" else "🟡"
            st.markdown(f"**Overall Status:** {status_color} {overall_status}")
            
            with st.expander("Detailed Breakdown"):
                st.json(feas_result)
        else:
            st.error(f"Feasibility evaluation failed: {feas_result['error']}")
        
        # Grounding Evaluation
        ground_result = results.get("grounding", {})
        if "error" not in ground_result:
            st.markdown("### 📚 Grounding Evaluation")
            overall_status = ground_result.get("overall_status", "Unknown")
            status_color = "🟢" if overall_status == "GROUNDED" else "🔴"
            st.markdown(f"**Overall Status:** {status_color} {overall_status}")
            
            with st.expander("Detailed Breakdown"):
                st.json(ground_result)
        else:
            st.error(f"Grounding evaluation failed: {ground_result['error']}")
            
        # Edit Correctness Evaluation (only show if available)
        if "edit_correctness" in results:
            edit_result = results.get("edit_correctness", {})
            if "error" not in edit_result:
                st.markdown("### ✅ Edit Correctness Evaluation")
                overall_status = edit_result.get("overall_status", "Unknown")
                status_color = "🟢" if overall_status == "CORRECT" else "🔴"
                st.markdown(f"**Overall Status:** {status_color} {overall_status}")
                
                with st.expander("Detailed Breakdown"):
                    st.json(edit_result)
            else:
                st.error(f"Edit correctness evaluation failed: {edit_result['error']}")
else:
    st.info("No active trip to evaluate. Generate a trip first to run evaluations.")

# Add footer
st.divider()
st.caption("AI Travel Assistant powered by FastAPI and Google Generative AI")
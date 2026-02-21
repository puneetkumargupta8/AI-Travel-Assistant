from fastapi import FastAPI, Body
from app.state import TripState
from app.mcp.poi_search import search_pois, POISearchInput
from app.mcp.travel_time import estimate_travel_time, TravelTimeInput
from app.mcp.itinerary_builder import build_itinerary
from app.state import TripConstraints
from app.orchestrator import Orchestrator
from app.evals.edit_correctness import evaluate_edit_correctness
from app.evals.feasibility import evaluate_feasibility
from app.evals.grounding import evaluate_grounding
from app.intents import classify_intent
from app.mcp.weather import get_delhi_weather
import copy
import requests
import os

app = FastAPI()
orchestrator = Orchestrator()

@app.get("/")
def health_check():
    return {"status": "running"}

@app.get("/test-state")
def test_state():
    example = TripState(
        city="Delhi",
        interests=["history", "food"],
        constraints={
            "days": 2,
            "pace": "relaxed"
        },
        days=[]
    )
    return example

@app.get("/test-itinerary")
def test_itinerary():
    poi_input = POISearchInput(
        city="Delhi",
        interests=["history", "food"],
        max_results=15
    )

    pois = search_pois(poi_input)

    constraints = TripConstraints(
        days=2,
        pace="relaxed"
    )

    itinerary = build_itinerary(pois, constraints)

    return itinerary

@app.get("/test-travel")
def test_travel():
    input_data = TravelTimeInput(
        lat1=28.5933,   # Humayun's Tomb approx
        lon1=77.2507,
        lat2=28.5244,   # Qutub Minar approx
        lon2=77.1855
    )

    result = estimate_travel_time(input_data)
    return result

@app.post("/plan-trip")
def plan_trip(payload: dict = Body(...)):
    city = payload.get("city")
    interests = payload.get("interests")
    days = payload.get("days")
    pace = payload.get("pace")

    trip = orchestrator.plan_trip(
        city=city,
        interests=interests,
        days=days,
        pace=pace
    )

    return trip

@app.post("/edit-day")
def edit_day(payload: dict = Body(...)):
    day_number = payload.get("day")
    new_pace = payload.get("pace")

    before_state = copy.deepcopy(orchestrator.current_trip)

    updated_trip = orchestrator.edit_day_pace(
        day_number=day_number,
        new_pace=new_pace
    )

    eval_result = evaluate_edit_correctness(
        before=before_state,
        after=updated_trip,
        intended_day=day_number
    )

    return {
        "trip": updated_trip,
        "edit_eval": eval_result
    }

@app.get("/run-feasibility")
def run_feasibility():
    if not orchestrator.current_trip:
        return {"error": "No active trip"}

    result = evaluate_feasibility(orchestrator.current_trip)
    return result

@app.get("/run-grounding")
def run_grounding():
    if not orchestrator.current_trip:
        return {"error": "No active trip"}

    result = evaluate_grounding(orchestrator.current_trip)
    return result

@app.post("/voice-command")
def voice_command(payload: dict = Body(...)):

    user_text = payload.get("text")

    intent_data = classify_intent(user_text)

    if "error" in intent_data:
        return intent_data

    intent = intent_data.get("intent")

    # PLAN FLOW
    if intent == "PLAN":
        trip = orchestrator.plan_trip(
            city=intent_data.get("city"),
            interests=intent_data.get("interests"),
            days=intent_data.get("days"),
            pace=intent_data.get("pace")
        )

        return {
            "intent": "PLAN",
            "trip": trip
        }

    # EDIT FLOW
    elif intent == "EDIT_DAY_PACE":
        if not orchestrator.current_trip:
            return {"error": "No active trip to edit."}

        updated_trip = orchestrator.edit_day_pace(
            day_number=intent_data.get("day"),
            new_pace=intent_data.get("pace")
        )

        return {
            "intent": "EDIT_DAY_PACE",
            "trip": updated_trip
        }

    # WEATHER ADJUSTMENT FLOW (check for rain-related query)
    elif intent == "EXPLAIN" and "rain" in user_text.lower():
        updated_trip = orchestrator.apply_weather_adjustment()

        return {
            "intent": "WEATHER_ADJUSTMENT",
            "trip": updated_trip
        }

    # EXPLAIN FLOW
    elif intent == "EXPLAIN":
        explanation = orchestrator.explain(
            target=intent_data.get("target")
        )

        return {
            "intent": "EXPLAIN",
            "explanation": explanation
        }

    else:
        return {"error": "Unsupported intent", "intent_data": intent_data}


@app.get("/test-weather")
def test_weather():
    return get_delhi_weather()


@app.post("/export-itinerary")
def export_itinerary(payload: dict = Body(...)):

    email = payload.get("email")

    if not orchestrator.current_trip:
        return {"error": "No active trip to export."}

    webhook_url = os.getenv("N8N_WEBHOOK_URL")

    if not webhook_url:
        return {"error": "N8N webhook URL not configured."}

    try:
        response = requests.post(
            webhook_url,
            json={
                "email": email,
                "trip": orchestrator.current_trip.dict()
            },
            timeout=10
        )

        return {
            "status": "sent",
            "n8n_response": response.text
        }

    except Exception as e:
        return {
            "error": "Failed to send to n8n",
            "details": str(e)
        }
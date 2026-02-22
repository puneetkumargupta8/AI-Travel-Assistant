from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import requests
import os
import time
from dotenv import load_dotenv

# Import our modules
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
from app.models import ExportRequest, ErrorResponse, SuccessResponse, HealthResponse
from app.config import config
from app.logging_config import logger, log_request, log_webhook_call, log_error
import copy

# Load environment variables
load_dotenv()

# Validate configuration
try:
    config.validate()
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    raise

app = FastAPI(title="AI Travel Assistant API", version="1.0.0")
orchestrator = Orchestrator()

# Exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            message="Invalid input data",
            details=str(exc)
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    log_error(logger, exc, "Unhandled exception")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="Internal server error",
            details="An unexpected error occurred"
        ).dict()
    )

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint for uptime monitoring"""
    return HealthResponse(status="ok")

# Existing endpoints (with improved error handling)
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
        raise HTTPException(status_code=400, detail="No active trip")

    result = evaluate_feasibility(orchestrator.current_trip)
    return result

@app.get("/run-grounding")
def run_grounding():
    if not orchestrator.current_trip:
        raise HTTPException(status_code=400, detail="No active trip")

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
            raise HTTPException(status_code=400, detail="No active trip to edit.")

        updated_trip = orchestrator.edit_day_pace(
            day_number=intent_data.get("day"),
            new_pace=intent_data.get("pace")
        )

        return {
            "intent": "EDIT_DAY_PACE",
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

# Improved export endpoint with production features
@app.post("/export-itinerary")
def export_itinerary(request: ExportRequest):
    """Export itinerary to n8n webhook with production-grade error handling"""
    
    # Log the request
    log_request(logger, "/export-itinerary", request.dict())
    
    # Validate active trip
    if not orchestrator.current_trip:
        logger.warning("Export attempt with no active trip")
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                message="No active trip to export",
                details="Generate a trip first before exporting"
            ).dict()
        )

    # Validate webhook URL configuration
    if not config.N8N_WEBHOOK_URL:
        logger.error("N8N webhook URL not configured")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                message="Service misconfigured",
                details="N8N webhook URL not configured"
            ).dict()
        )

    # Prepare webhook payload
    webhook_payload = {
        "email": request.email,
        "trip": orchestrator.current_trip.dict()
    }

    # Make webhook call with timeout and retry logic
    start_time = time.time()
    max_retries = config.MAX_RETRIES
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            logger.info(f"Calling n8n webhook (attempt {retry_count + 1})")
            
            response = requests.post(
                config.N8N_WEBHOOK_URL,
                json=webhook_payload,
                timeout=config.REQUEST_TIMEOUT
            )
            
            duration = time.time() - start_time
            log_webhook_call(logger, config.N8N_WEBHOOK_URL, "success", duration)
            
            # Return success response
            return SuccessResponse(
                message="Itinerary exported successfully",
                data={
                    "email": request.email,
                    "status": "sent",
                    "webhook_response": response.text[:200]  # Limit response size
                }
            )
            
        except requests.exceptions.Timeout as e:
            duration = time.time() - start_time
            log_webhook_call(logger, config.N8N_WEBHOOK_URL, "timeout", duration)
            
            retry_count += 1
            if retry_count <= max_retries:
                logger.warning(f"Webhook timeout, retrying... ({retry_count}/{max_retries})")
                time.sleep(1)  # Brief delay before retry
                continue
            else:
                log_error(logger, e, "Webhook timeout after retries")
                raise HTTPException(
                    status_code=504,
                    detail=ErrorResponse(
                        message="Webhook timeout",
                        details=f"Request timed out after {config.REQUEST_TIMEOUT} seconds"
                    ).dict()
                )
                
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            log_webhook_call(logger, config.N8N_WEBHOOK_URL, "error", duration)
            log_error(logger, e, "Webhook request failed")
            
            raise HTTPException(
                status_code=502,
                detail=ErrorResponse(
                    message="Webhook service unavailable",
                    details=str(e)
                ).dict()
            )
        except Exception as e:
            duration = time.time() - start_time
            log_webhook_call(logger, config.N8N_WEBHOOK_URL, "error", duration)
            log_error(logger, e, "Unexpected error in webhook call")
            
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    message="Failed to process export request",
                    details=str(e)
                ).dict()
            )

@app.get("/test-weather")
def test_weather():
    return get_delhi_weather()
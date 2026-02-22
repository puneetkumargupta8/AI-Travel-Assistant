# AI Travel Assistant

An AI-powered travel planning application that helps users create personalized itineraries based on their interests and preferences.

## Features

- AI-powered trip planning
- Personalized recommendations based on interests
- Flexible trip duration and pacing options
- Real-time itinerary adjustments
- Weather information integration

## Architecture

The application consists of two main components:

1. **Backend API**: Built with FastAPI, handles all business logic and AI processing
2. **Frontend Interface**: Built with Streamlit, provides a user-friendly interface

## Prerequisites

- Python 3.11 or higher
- Google AI API key (for generative AI features)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd AI-Travel-Assistant
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- On Windows:
```bash
venv\Scripts\activate
```
- On macOS/Linux:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:
Create a `.env` file in the root directory with your Google AI API key:
```
GOOGLE_API_KEY=your_google_api_key_here
```

## Running the Application

### Backend API Server

1. Navigate to the project directory and activate your virtual environment
2. Run the FastAPI server:
```bash
cd app
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`

### Streamlit Frontend

1. Make sure the backend API server is running
2. In a new terminal, navigate to the project directory and activate your virtual environment
3. Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```
The frontend will be available at `http://localhost:8501`

Or use the convenience script:
```bash
python run_streamlit.py
```

## Using the Application

1. Open the Streamlit frontend at `http://localhost:8501`
2. Configure your trip preferences in the sidebar:
   - City you want to visit
   - Your interests (history, food, culture, etc.)
   - Number of days for your trip
   - Desired pace (relaxed, moderate, packed)
3. Click "Generate Itinerary" to create your personalized trip plan
4. Review your itinerary day by day
5. Use the "Edit Day Pace" section to adjust the schedule for specific days

## API Endpoints

The backend exposes several API endpoints:

- `GET /` - Health check
- `POST /plan-trip` - Plan a new trip
- `POST /edit-day` - Edit the pace of a specific day
- `GET /test-weather` - Get weather information for Delhi
- `POST /voice-command` - Process voice commands (text input)

## Components

The application is organized into several modules:

- `mcp/` - Core AI components (POI search, travel time estimation, itinerary builder)
- `rag/` - Retrieval-Augmented Generation components
- `evals/` - Evaluation functions for quality assurance
- `state.py` - Data models for trip state
- `orchestrator.py` - Main orchestration logic
- `intents.py` - Natural language intent classification
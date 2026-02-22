from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
from app.state import TripState


class ExportRequest(BaseModel):
    """Request model for itinerary export endpoint"""
    email: EmailStr
    trip: Dict[str, Any]  # Using dict for flexibility with TripState


class ErrorResponse(BaseModel):
    """Standard error response model"""
    status: str = "error"
    message: str
    details: Optional[str] = None


class SuccessResponse(BaseModel):
    """Standard success response model"""
    status: str = "success"
    message: str
    data: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = "ok"
    timestamp: Optional[str] = None
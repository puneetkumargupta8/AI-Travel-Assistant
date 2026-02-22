import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from app.config import config

def setup_logging():
    """Setup application logging"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def log_request(logger: logging.Logger, endpoint: str, payload: Dict[str, Any]):
    """Log incoming request (without sensitive data)"""
    # Remove sensitive fields from logging
    safe_payload = payload.copy()
    if 'email' in safe_payload:
        safe_payload['email'] = "***@***.***"  # Mask email
    
    logger.info(f"Request to {endpoint}", extra={
        "endpoint": endpoint,
        "payload": json.dumps(safe_payload, default=str)
    })

def log_webhook_call(logger: logging.Logger, url: str, status: str, duration: float):
    """Log webhook call details"""
    logger.info("Webhook call", extra={
        "url": url,
        "status": status,
        "duration_ms": round(duration * 1000, 2)
    })

def log_error(logger: logging.Logger, error: Exception, context: Optional[str] = None):
    """Log errors with context"""
    logger.error(f"Error occurred: {str(error)}", extra={
        "error_type": type(error).__name__,
        "context": context,
        "timestamp": datetime.utcnow().isoformat()
    })

# Initialize logger
logger = setup_logging()
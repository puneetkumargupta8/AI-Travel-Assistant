import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Environment
    APP_ENV = os.getenv("APP_ENV", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # n8n Configuration
    N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "5"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "1"))
    
    # Backend Configuration
    BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
    BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
    
    # Validation
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.N8N_WEBHOOK_URL:
            raise ValueError("N8N_WEBHOOK_URL environment variable is required")
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")
    
    # Properties for convenience
    @property
    def is_development(self):
        return self.APP_ENV == "development"
    
    @property
    def is_production(self):
        return self.APP_ENV == "production"

# Initialize config
config = Config()
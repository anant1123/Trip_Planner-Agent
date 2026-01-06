"""
Configuration management for TripGenie
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class APIConfig:
    """API Configuration"""
    groq_api_key: str
    tavily_api_key: str
    langchain_tracing: bool = True
    langchain_project: str = "TripGenie_Agent"
    
    def validate(self) -> None:
        """Validate API keys"""
        missing = []
        if not self.groq_api_key:
            missing.append("GROQ_API_KEY")
        if not self.tavily_api_key:
            missing.append("TAVILY_API_KEY")
        
        if missing:
            raise ValueError(
                f"Missing required API keys: {', '.join(missing)}. "
                "Please set them in your .env file."
            )


@dataclass
class ModelConfig:
    """LLM Model Configuration"""
    model_name: str = "llama-3.3-70b-versatile"
    temperature: float = 0.4
    max_retries: int = 2
    max_tokens: Optional[int] = None
    timeout: int = 120


@dataclass
class SearchConfig:
    """Search Tool Configuration"""
    tavily_max_results: int = 3
    enable_ddg_fallback: bool = True
    request_timeout: int = 30


@dataclass
class LocationConfig:
    """Location Service Configuration"""
    nominatim_url: str = "https://nominatim.openstreetmap.org/search"
    user_agent: str = "TripGenie-Education-Project-v1.0"
    rate_limit_delay: float = 1.0
    max_results: int = 5
    timeout: int = 10


@dataclass
class UIConfig:
    """UI Configuration"""
    page_title: str = "TripGenie - AI Travel Planner"
    page_icon: str = "🌍"
    layout: str = "centered"
    max_people: int = 20
    max_days: int = 30
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour


class Settings:
    """Main settings class"""
    
    def __init__(self):
        self.api = APIConfig(
            groq_api_key=os.getenv("GROQ_API_KEY", ""),
            tavily_api_key=os.getenv("TAVILY_API_KEY", "")
        )
        self.model = ModelConfig()
        self.search = SearchConfig()
        self.location = LocationConfig()
        self.ui = UIConfig()
        
        # Validate on initialization
        self.api.validate()
        
        # Setup LangChain tracing
        if self.api.langchain_tracing:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_PROJECT"] = self.api.langchain_project
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return os.getenv("ENVIRONMENT", "development") == "development"
    
    @property
    def version(self) -> str:
        """Get application version"""
        return "1.0.0"


# Global settings instance
settings = Settings()

"""
Location search service using OpenStreetMap Nominatim
"""
import time
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Location:
    """Location data model"""
    name: str
    label: str
    lat: float
    lon: float
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    
    @classmethod
    def from_nominatim(cls, data: Dict) -> 'Location':
        """
        Create Location from Nominatim API response
        
        Args:
            data: Nominatim API response dictionary
            
        Returns:
            Location instance
        """
        address = data.get("address", {})
        display_name = data.get("display_name", "")
        
        return cls(
            name=display_name,
            label=display_name,
            lat=float(data.get("lat", 0)),
            lon=float(data.get("lon", 0)),
            city=address.get("city") or address.get("town") or address.get("village"),
            state=address.get("state"),
            country=address.get("country")
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def __str__(self) -> str:
        """String representation"""
        parts = []
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts) if parts else self.label


class LocationService:
    """Service for location search operations"""
    
    def __init__(self):
        """Initialize location service with configuration"""
        self.base_url = settings.location.nominatim_url
        self.user_agent = settings.location.user_agent
        self.rate_limit_delay = settings.location.rate_limit_delay
        self.max_results = settings.location.max_results
        self.timeout = settings.location.timeout
        self._last_request_time = 0
        
        logger.info("LocationService initialized")
    
    def _respect_rate_limit(self) -> None:
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()
    
    def search(self, query: str) -> List[Location]:
        """
        Search for locations by query string
        
        Args:
            query: Search query (e.g., "Paris", "New York, USA")
            
        Returns:
            List of Location objects
        """
        if not query or not query.strip():
            logger.warning("Empty search query")
            return []
        
        try:
            self._respect_rate_limit()
            
            params = {
                "q": query.strip(),
                "format": "json",
                "addressdetails": 1,
                "limit": self.max_results
            }
            
            headers = {
                "User-Agent": self.user_agent
            }
            
            logger.info(f"Searching location: {query}")
            start_time = time.time()
            
            response = requests.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            duration = time.time() - start_time
            results = response.json()
            locations = [Location.from_nominatim(r) for r in results]
            
            logger.log_search(query, len(locations), duration)
            
            return locations
            
        except requests.Timeout:
            logger.error(f"Location search timeout for query: {query}")
            return []
        except requests.RequestException as e:
            logger.error(f"Location search failed for '{query}'", exc=e)
            return []
        except Exception as e:
            logger.error(f"Unexpected error in location search", exc=e)
            return []
    
    def get_coordinates(self, query: str) -> Optional[tuple[float, float]]:
        """
        Get latitude and longitude for a location
        
        Args:
            query: Location query
            
        Returns:
            Tuple of (lat, lon) or None if not found
        """
        locations = self.search(query)
        if locations:
            return (locations[0].lat, locations[0].lon)
        return None
    
    def get_location_details(self, query: str) -> Optional[Location]:
        """
        Get detailed information for a location
        
        Args:
            query: Location query
            
        Returns:
            Location object or None if not found
        """
        locations = self.search(query)
        if locations:
            return locations[0]
        return None

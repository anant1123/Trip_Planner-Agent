"""
Storage service for trip history
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TripRecord:
    """Trip record data model"""
    id: str
    timestamp: str
    from_city: str
    to_city: str
    days: int
    people: int
    group_type: str
    trip_plan: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TripRecord':
        """Create from dictionary"""
        return cls(**data)


class TripStorage:
    """Service for storing and retrieving trip history"""
    
    def __init__(self, storage_path: str = "data/trip_history.json"):
        """
        Initialize storage service
        
        Args:
            storage_path: Path to storage file
        """
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(exist_ok=True)
        
        # Initialize file if it doesn't exist
        if not self.storage_path.exists():
            self._write_data([])
        
        logger.info(f"TripStorage initialized: {storage_path}")
    
    def _read_data(self) -> List[Dict]:
        """Read data from storage file"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from storage file")
            return []
        except Exception as e:
            logger.error(f"Failed to read storage file", exc=e)
            return []
    
    def _write_data(self, data: List[Dict]) -> bool:
        """Write data to storage file"""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to write to storage file", exc=e)
            return False
    
    def save_trip(
        self,
        from_city: str,
        to_city: str,
        days: int,
        people: int,
        group_type: str,
        trip_plan: str
    ) -> Optional[str]:
        """
        Save a trip record
        
        Args:
            from_city: Departure city
            to_city: Destination city
            days: Trip duration
            people: Number of travelers
            group_type: Type of group (Solo, Couple, etc.)
            trip_plan: Generated trip plan
            
        Returns:
            Trip ID if successful, None otherwise
        """
        try:
            trip_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            timestamp = datetime.now().isoformat()
            
            trip_record = TripRecord(
                id=trip_id,
                timestamp=timestamp,
                from_city=from_city,
                to_city=to_city,
                days=days,
                people=people,
                group_type=group_type,
                trip_plan=trip_plan
            )
            
            data = self._read_data()
            data.append(trip_record.to_dict())
            
            if self._write_data(data):
                logger.info(f"Trip saved successfully: {trip_id}")
                return trip_id
            else:
                return None
                
        except Exception as e:
            logger.error("Failed to save trip", exc=e)
            return None
    
    def get_trip(self, trip_id: str) -> Optional[TripRecord]:
        """
        Get a specific trip by ID
        
        Args:
            trip_id: Trip ID
            
        Returns:
            TripRecord if found, None otherwise
        """
        try:
            data = self._read_data()
            for record in data:
                if record.get('id') == trip_id:
                    return TripRecord.from_dict(record)
            return None
        except Exception as e:
            logger.error(f"Failed to get trip {trip_id}", exc=e)
            return None
    
    def get_all_trips(self, limit: Optional[int] = None) -> List[TripRecord]:
        """
        Get all trip records
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of TripRecord objects
        """
        try:
            data = self._read_data()
            # Sort by timestamp descending (newest first)
            data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            if limit:
                data = data[:limit]
            
            return [TripRecord.from_dict(record) for record in data]
        except Exception as e:
            logger.error("Failed to get all trips", exc=e)
            return []
    
    def delete_trip(self, trip_id: str) -> bool:
        """
        Delete a trip record
        
        Args:
            trip_id: Trip ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = self._read_data()
            original_length = len(data)
            
            data = [record for record in data if record.get('id') != trip_id]
            
            if len(data) < original_length:
                if self._write_data(data):
                    logger.info(f"Trip deleted: {trip_id}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to delete trip {trip_id}", exc=e)
            return False
    
    def clear_all(self) -> bool:
        """
        Clear all trip records
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self._write_data([]):
                logger.info("All trips cleared")
                return True
            return False
        except Exception as e:
            logger.error("Failed to clear trips", exc=e)
            return False
    
    def export_trip_to_text(self, trip_id: str, output_path: str) -> bool:
        """
        Export trip plan to text file
        
        Args:
            trip_id: Trip ID
            output_path: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            trip = self.get_trip(trip_id)
            if not trip:
                return False
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"TripGenie Trip Plan\n")
                f.write(f"=" * 80 + "\n\n")
                f.write(f"From: {trip.from_city}\n")
                f.write(f"To: {trip.to_city}\n")
                f.write(f"Duration: {trip.days} days\n")
                f.write(f"Travelers: {trip.people} ({trip.group_type})\n")
                f.write(f"Generated: {trip.timestamp}\n\n")
                f.write("=" * 80 + "\n\n")
                f.write(trip.trip_plan)
            
            logger.info(f"Trip exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export trip {trip_id}", exc=e)
            return False

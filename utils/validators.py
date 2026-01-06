"""
Input validation utilities
"""
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
import re


class ValidationError(Exception):
    """Custom validation error"""
    pass


class TripValidator:
    """Validator for trip planning inputs"""
    
    @staticmethod
    def validate_location(location: str, field_name: str = "Location") -> bool:
        """
        Validate location input
        
        Args:
            location: Location string to validate
            field_name: Name of the field for error messages
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If validation fails
        """
        if not location or not location.strip():
            raise ValidationError(f"{field_name} cannot be empty")
        
        location = location.strip()
        
        if len(location) < 2:
            raise ValidationError(f"{field_name} must be at least 2 characters")
        
        if len(location) > 100:
            raise ValidationError(f"{field_name} name is too long (max 100 characters)")
        
        # Check for suspicious patterns
        if re.search(r'[<>{}[\]\\]', location):
            raise ValidationError(f"{field_name} contains invalid characters")
        
        return True
    
    @staticmethod
    def validate_people_count(count: int) -> bool:
        """
        Validate number of travelers
        
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(count, int):
            raise ValidationError("Number of travelers must be a number")
        
        if count < 1:
            raise ValidationError("At least 1 traveler is required")
        
        if count > 50:
            raise ValidationError("Maximum 50 travelers allowed")
        
        return True
    
    @staticmethod
    def validate_days(days: int) -> bool:
        """
        Validate trip duration
        
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(days, int):
            raise ValidationError("Trip duration must be a number")
        
        if days < 1:
            raise ValidationError("Trip must be at least 1 day")
        
        if days > 365:
            raise ValidationError("Maximum trip duration is 365 days")
        
        return True
    
    @staticmethod
    def validate_same_location(from_loc: str, to_loc: str) -> bool:
        """
        Validate that departure and destination are different
        
        Raises:
            ValidationError: If locations are the same
        """
        if from_loc.lower().strip() == to_loc.lower().strip():
            raise ValidationError("Departure and destination cannot be the same")
        
        return True
    
    @staticmethod
    def validate_date_range(
        start_date: datetime,
        end_date: datetime
    ) -> bool:
        """
        Validate date range
        
        Raises:
            ValidationError: If date range is invalid
        """
        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if start_date < now:
            raise ValidationError("Start date cannot be in the past")
        
        if end_date <= start_date:
            raise ValidationError("End date must be after start date")
        
        if (end_date - start_date).days > 365:
            raise ValidationError("Trip duration exceeds 365 days")
        
        return True
    
    @staticmethod
    def validate_budget(budget_str: str) -> Tuple[float, float]:
        """
        Parse and validate budget string
        
        Args:
            budget_str: Budget string like "₹1000-3000 / €10-30"
            
        Returns:
            Tuple of (min_budget, max_budget)
            
        Raises:
            ValidationError: If budget is invalid
        """
        try:
            # Extract numbers from budget string
            numbers = re.findall(r'\d+', budget_str)
            
            if len(numbers) >= 2:
                min_budget = float(numbers[0])
                max_budget = float(numbers[1])
                
                if min_budget < 0 or max_budget < 0:
                    raise ValidationError("Budget cannot be negative")
                
                if min_budget > max_budget:
                    raise ValidationError("Invalid budget range")
                
                return (min_budget, max_budget)
            
            # No limit case
            if "luxury" in budget_str.lower() or "no limit" in budget_str.lower():
                return (0, float('inf'))
            
            return (0, float('inf'))
            
        except ValueError:
            raise ValidationError("Invalid budget format")
    
    @staticmethod
    def sanitize_text_input(text: str, max_length: int = 500) -> str:
        """
        Sanitize user text input
        
        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove script tags and content
        text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Trim whitespace
        text = text.strip()
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text
    
    @staticmethod
    def validate_complete_trip_input(trip_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate all trip input data
        
        Args:
            trip_data: Dictionary with all trip parameters
            
        Returns:
            Validated and sanitized trip data
            
        Raises:
            ValidationError: If any validation fails
        """
        errors = []
        
        # Validate locations
        try:
            TripValidator.validate_location(trip_data.get('from_city', ''), "Departure location")
        except ValidationError as e:
            errors.append(str(e))
        
        try:
            TripValidator.validate_location(trip_data.get('to_city', ''), "Destination")
        except ValidationError as e:
            errors.append(str(e))
        
        # Validate they're different
        if trip_data.get('from_city') and trip_data.get('to_city'):
            try:
                TripValidator.validate_same_location(
                    trip_data['from_city'],
                    trip_data['to_city']
                )
            except ValidationError as e:
                errors.append(str(e))
        
        # Validate people and days
        try:
            TripValidator.validate_people_count(trip_data.get('people', 0))
        except ValidationError as e:
            errors.append(str(e))
        
        try:
            TripValidator.validate_days(trip_data.get('days', 0))
        except ValidationError as e:
            errors.append(str(e))
        
        # Sanitize text inputs
        if 'notes' in trip_data:
            trip_data['notes'] = TripValidator.sanitize_text_input(
                trip_data['notes'],
                max_length=1000
            )
        
        # If there are errors, raise them all
        if errors:
            raise ValidationError("\n".join(errors))
        
        return trip_data
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format
        
        Raises:
            ValidationError: If email is invalid
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format")
        
        return True

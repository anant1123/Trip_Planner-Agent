"""
TripGenie - AI Travel Planner
Main entry point
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logging, get_logger
from config.settings import settings

# Setup logging
setup_logging()
logger = get_logger(__name__)

logger.info("=" * 80)
logger.info(f"TripGenie v{settings.version} - Starting")
logger.info("=" * 80)


def main():
    """Main entry point"""
    try:
        from services.agent_service import TripGenieAgent
        from services.location_service import LocationService
        
        logger.info("Initializing services...")
        
        agent = TripGenieAgent()
        location_service = LocationService()
        
        logger.info("Services initialized successfully")
        logger.info("TripGenie is ready!")
        
        # Example usage
        print("\n" + "=" * 80)
        print("TripGenie - AI Travel Planner")
        print("=" * 80)
        print("\nTo run the web interface:")
        print("  streamlit run ui/app.py")
        print("\nFor programmatic usage, import:")
        print("  from services.agent_service import TripGenieAgent")
        print("  agent = TripGenieAgent()")
        print("  plan = agent.generate_trip_plan('Your query here')")
        print("=" * 80 + "\n")
        
    except Exception as e:
        logger.error("Failed to initialize TripGenie", exc=e)
        print(f"\n❌ Error: {e}")
        print("Please check your .env file and ensure all API keys are set.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

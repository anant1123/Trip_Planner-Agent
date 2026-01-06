"""
Enhanced Streamlit UI for TripGenie
"""
import streamlit as st
import time
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.location_service import LocationService
from services.agent_service import TripGenieAgent
from services.storage_service import TripStorage
from utils.validators import TripValidator, ValidationError
from utils.logger import setup_logging, get_logger
from utils.formatters import format_duration
from config.settings import settings

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize services
@st.cache_resource
def get_location_service():
    """Get cached location service"""
    return LocationService()

@st.cache_resource
def get_agent():
    """Get cached agent"""
    return TripGenieAgent()

@st.cache_resource
def get_storage():
    """Get cached storage service"""
    return TripStorage()

try:
    location_service = get_location_service()
    agent = get_agent()
    storage = get_storage()
    logger.info("All services initialized successfully")
except Exception as e:
    st.error(f"Failed to initialize services: {e}")
    logger.error("Service initialization failed", exc=e)
    st.stop()


# =============================
#   PAGE CONFIGURATION
# =============================
st.set_page_config(
    page_title=settings.ui.page_title,
    page_icon=settings.ui.page_icon,
    layout=settings.ui.layout,
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(120deg, #1E88E5, #42A5F5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(120deg, #1E88E5, #42A5F5);
        color: white;
        font-weight: bold;
        padding: 0.7rem 1rem;
        border-radius: 10px;
        border: none;
        font-size: 1.1rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(30, 136, 229, 0.4);
    }
    .trip-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
    .stats-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1E88E5;
    }
</style>
""", unsafe_allow_html=True)


# =============================
#   HEADER
# =============================
st.markdown('<div class="main-header">🌍 TripGenie</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Your AI-Powered Travel Planning Assistant ✈️</div>',
    unsafe_allow_html=True
)


# =============================
#   SIDEBAR
# =============================
with st.sidebar:
    st.header("ℹ️ About TripGenie")
    st.info(f"""
**Version**: {settings.version}

TripGenie is an educational AI travel planner powered by:
- 🤖 LangGraph & LangChain
- 🔍 Real-time search (Tavily + DuckDuckGo)
- 🗺️ OpenStreetMap location search
- 📝 Trip history & export

**Features:**
✅ Smart itinerary generation  
✅ Real-time price search  
✅ Budget-friendly recommendations  
✅ Save & export trip plans  
""")
    
    st.markdown("---")
    
    st.header("⚙️ Settings")
    show_debug = st.checkbox("Show debug info", value=False)
    save_history = st.checkbox("Save trip history", value=True)
    
    if show_debug:
        st.json({
            "model": settings.model.model_name,
            "temperature": settings.model.temperature,
            "search_tools": len(agent.tools),
            "tracing": settings.api.langchain_tracing
        })


# =============================
#   MAIN TABS
# =============================
tab1, tab2, tab3 = st.tabs(["🗺️ Plan Trip", "📚 Trip History", "💡 Tips & Guide"])

# =============================
#   TAB 1: PLAN TRIP
# =============================
with tab1:
    st.header("📍 Where are you going?")
    
    col1, col2 = st.columns(2)
    
    # Departure location
    with col1:
        from_input = st.text_input(
            "From (Departure City)",
            placeholder="e.g., Mumbai, Delhi, London",
            help="Start typing your city name",
            key="from_input"
        )
        
        from_selected = None
        from_location = None
        
        if from_input and len(from_input) >= 2:
            with st.spinner("🔍 Searching locations..."):
                try:
                    from_results = location_service.search(from_input)
                    
                    if from_results:
                        from_labels = [loc.label for loc in from_results]
                        from_selected = st.selectbox(
                            "Confirm departure location",
                            from_labels,
                            key="from_select"
                        )
                        # Get the actual location object
                        from_location = from_results[from_labels.index(from_selected)]
                    else:
                        st.warning("⚠️ No locations found. Try a different search.")
                        
                except Exception as e:
                    st.error(f"❌ Location search failed: {e}")
                    logger.error("Departure location search failed", exc=e)
    
    # Destination
    with col2:
        to_input = st.text_input(
            "To (Destination)",
            placeholder="e.g., Paris, Tokyo, Bali",
            help="Where do you want to go?",
            key="to_input"
        )
        
        to_selected = None
        to_location = None
        
        if to_input and len(to_input) >= 2:
            with st.spinner("🔍 Searching locations..."):
                try:
                    to_results = location_service.search(to_input)
                    
                    if to_results:
                        to_labels = [loc.label for loc in to_results]
                        to_selected = st.selectbox(
                            "Confirm destination",
                            to_labels,
                            key="to_select"
                        )
                        # Get the actual location object
                        to_location = to_results[to_labels.index(to_selected)]
                    else:
                        st.warning("⚠️ No locations found. Try a different search.")
                        
                except Exception as e:
                    st.error(f"❌ Location search failed: {e}")
                    logger.error("Destination search failed", exc=e)
    
    st.markdown("---")
    
    # Trip Details
    st.header("📅 Trip Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        people = st.number_input(
            "Number of Travelers",
            min_value=1,
            max_value=settings.ui.max_people,
            value=2,
            help="How many people are traveling?"
        )
    
    with col2:
        days = st.number_input(
            "Trip Duration (days)",
            min_value=1,
            max_value=settings.ui.max_days,
            value=3,
            help="How long is your trip?"
        )
    
    with col3:
        group_type = st.selectbox(
            "Travel Group",
            ["Solo", "Couple", "Friends", "Family", "Business"],
            help="Who are you traveling with?"
        )
    
    st.markdown("---")
    
    # Preferences
    st.header("🎯 Your Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        transport = st.radio(
            "🚗 Primary Transport",
            ["Flight", "Train", "Bus/Road Trip", "Any"],
            horizontal=True
        )
        
        hotel_budget = st.select_slider(
            "💰 Hotel Budget (per night)",
            options=[
                "Budget (₹0-1000)",
                "Economy (₹1000-3000)",
                "Mid-Range (₹3000-6000)",
                "Premium (₹6000-12000)",
                "Luxury (₹12000+)"
            ],
            value="Economy (₹1000-3000)"
        )
    
    with col2:
        food_pref = st.multiselect(
            "🍽️ Food Preferences",
            ["Vegetarian", "Non-Veg", "Vegan", "Local Cuisine", 
             "Street Food", "Fine Dining", "Cafe Hopping"],
            default=["Local Cuisine"]
        )
        
        trip_style = st.multiselect(
            "🎨 Trip Style",
            ["Budget Friendly", "Luxury", "Adventure", "Relaxation",
             "Culture & History", "Nature", "Nightlife", "Photography"],
            default=["Budget Friendly"],
            help="Select multiple styles"
        )
    
    # Advanced Options
    with st.expander("🔧 Advanced Options"):
        pace = st.radio(
            "Trip Pace",
            ["Relaxed (2-3 activities/day)", 
             "Balanced (3-5 activities/day)", 
             "Packed (5+ activities/day)"],
            index=1
        )
        
        stay_type = st.multiselect(
            "Accommodation Type",
            ["Hotel", "Hostel", "Airbnb", "Resort", "Guest House"],
            default=["Hotel"]
        )
        
        special_notes = st.text_area(
            "Special Requirements",
            placeholder="Example: Wheelchair accessible, senior citizens, honeymoon, dietary restrictions, etc.",
            max_chars=1000,
            help="Any special requirements or notes"
        )
    
    st.markdown("---")
    
    # Generate Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button(
            "✨ Generate My Trip Plan",
            type="primary",
            use_container_width=True
        )
    
    # Process trip generation
    if generate_button:
        try:
            # Validation
            if not from_selected or not to_selected:
                st.error("❌ Please select both departure and destination locations")
                logger.warning("Trip generation attempted without both locations")
            else:
                # Validate inputs
                trip_data = {
                    'from_city': from_selected,
                    'to_city': to_selected,
                    'people': people,
                    'days': days,
                    'notes': special_notes
                }
                
                TripValidator.validate_complete_trip_input(trip_data)
                
                # Log user action
                logger.log_user_action(
                    "generate_trip",
                    from_city=from_selected,
                    to_city=to_selected,
                    days=days,
                    people=people,
                    group_type=group_type
                )
                
                # Build prompt
                prompt = f"""Plan a detailed {days}-day trip for {people} {group_type.lower()} traveler(s).

ROUTE: {from_selected} → {to_selected}

TRANSPORT: {transport}
BUDGET: {hotel_budget} per night
ACCOMMODATION: {', '.join(stay_type)}

FOOD PREFERENCES: {', '.join(food_pref) if food_pref else 'Any'}
TRIP STYLE: {', '.join(trip_style) if trip_style else 'Balanced'}
PACE: {pace}

SPECIAL REQUIREMENTS: {special_notes if special_notes else 'None'}

Please provide:
1. Detailed day-by-day itinerary with specific activities
2. Estimated costs (flights, hotels, food, activities) with sources
3. Best time to visit and weather considerations
4. Important tips and local recommendations
5. Transportation options within the destination
6. Safety and cultural tips

Be specific, cite all sources, and provide real prices where possible.
"""
                
                # Generate plan with progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🤖 Initializing TripGenie...")
                progress_bar.progress(10)
                time.sleep(0.5)
                
                status_text.text("🔍 Searching for best options...")
                progress_bar.progress(30)
                
                start_time = time.time()
                
                try:
                    response = agent.generate_trip_plan(prompt)
                    
                    duration = time.time() - start_time
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Trip plan ready!")
                    time.sleep(0.5)
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Log successful generation
                    logger.log_trip_generation(
                        from_selected,
                        to_selected,
                        days,
                        "success",
                        duration
                    )
                    
                    # Display results
                    st.success(f"✅ Trip plan generated in {duration:.1f} seconds!")
                    
                    st.markdown("---")
                    st.header("🗺️ Your Personalized Trip Plan")
                    st.markdown(response)
                    
                    # Save to history
                    if save_history:
                        trip_id = storage.save_trip(
                            from_city=from_selected,
                            to_city=to_selected,
                            days=days,
                            people=people,
                            group_type=group_type,
                            trip_plan=response
                        )
                        if trip_id:
                            st.success(f"💾 Trip saved to history (ID: {trip_id})")
                        else:
                            st.warning("⚠️ Could not save trip to history")
                    
                    # Download options
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            label="📥 Download as Text",
                            data=response,
                            file_name=f"tripgenie_{to_input}_{days}days_{datetime.now():%Y%m%d}.txt",
                            mime="text/plain"
                        )
                    
                    with col2:
                        # Create formatted version for download
                        formatted_plan = f"""
TripGenie Trip Plan
{'=' * 80}

From: {from_selected}
To: {to_selected}
Duration: {format_duration(days)}
Travelers: {people} ({group_type})
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

{'=' * 80}

{response}

{'=' * 80}
Generated by TripGenie - AI Travel Planner
https://tripgenie.app
"""
                        st.download_button(
                            label="📄 Download Formatted",
                            data=formatted_plan,
                            file_name=f"tripgenie_{to_input}_{days}days_{datetime.now():%Y%m%d}_formatted.txt",
                            mime="text/plain"
                        )
                    
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"❌ Error generating trip: {str(e)}")
                    logger.error("Trip generation failed", exc=e)
                    
                    if show_debug:
                        st.exception(e)
                
        except ValidationError as e:
            st.error(f"❌ Validation Error:\n{str(e)}")
            logger.warning(f"Validation error: {e}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            logger.error("Unexpected error in trip generation", exc=e)
            
            if show_debug:
                st.exception(e)

# =============================
#   TAB 2: TRIP HISTORY
# =============================
with tab2:
    st.header("📚 Your Trip History")
    
    if not save_history:
        st.info("ℹ️ Trip history saving is disabled. Enable it in the sidebar settings.")
    else:
        try:
            trips = storage.get_all_trips(limit=50)
            
            if not trips:
                st.info("📭 No trip history yet. Generate your first trip plan!")
            else:
                st.success(f"📊 Found {len(trips)} saved trip(s)")
                
                for trip in trips:
                    with st.expander(
                        f"🗺️ {trip.from_city} → {trip.to_city} | "
                        f"{trip.days} days | {trip.people} travelers | "
                        f"{datetime.fromisoformat(trip.timestamp).strftime('%b %d, %Y')}"
                    ):
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.write(f"**From:** {trip.from_city}")
                            st.write(f"**To:** {trip.to_city}")
                        
                        with col2:
                            st.write(f"**Duration:** {format_duration(trip.days)}")
                            st.write(f"**Group:** {trip.people} {trip.group_type}")
                        
                        with col3:
                            if st.button("🗑️ Delete", key=f"del_{trip.id}"):
                                if storage.delete_trip(trip.id):
                                    st.success("✅ Deleted!")
                                    st.rerun()
                                else:
                                    st.error("❌ Delete failed")
                        
                        st.markdown("---")
                        st.markdown(trip.trip_plan)
                        
                        st.download_button(
                            label="📥 Download",
                            data=trip.trip_plan,
                            file_name=f"trip_{trip.id}.txt",
                            mime="text/plain",
                            key=f"dl_{trip.id}"
                        )
                
                st.markdown("---")
                if st.button("🗑️ Clear All History", type="secondary"):
                    if storage.clear_all():
                        st.success("✅ All history cleared!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to clear history")
        
        except Exception as e:
            st.error(f"❌ Error loading trip history: {e}")
            logger.error("Failed to load trip history", exc=e)

# =============================
#   TAB 3: TIPS & GUIDE
# =============================
with tab3:
    st.header("💡 Travel Planning Tips & Guide")
    
    st.markdown("""
    ### 🎯 How to Get the Best Results
    
    1. **Be Specific**: The more details you provide, the better your itinerary
    2. **Flexible Dates**: Consider traveling mid-week for better deals
    3. **Book Early**: Flights and hotels are cheaper when booked in advance
    4. **Local Research**: TripGenie uses real-time search but always verify prices
    5. **Budget Buffer**: Add 10-20% extra to your budget for unexpected expenses
    
    ### 💰 Budget Travel Tips
    
    - **Flights**: Use budget airlines, be flexible with dates, book 2-3 months ahead
    - **Accommodation**: Consider hostels, Airbnb, or homestays
    - **Food**: Eat at local restaurants away from tourist areas
    - **Transport**: Use public transportation instead of taxis
    - **Activities**: Look for free walking tours and city passes
    
    ### 🔒 Safety Tips
    
    - Register with your embassy when traveling abroad
    - Keep copies of important documents (passport, visa, insurance)
    - Get comprehensive travel insurance
    - Research local customs, laws, and scams
    - Share your itinerary with family/friends
    - Keep emergency contact numbers handy
    
    ### 📱 Using TripGenie Effectively
    
    **Location Search:**
    - Type at least 2 characters to start searching
    - Be specific (e.g., "Paris, France" vs just "Paris")
    - Select from the dropdown to confirm location
    
    **Trip Preferences:**
    - Select multiple trip styles for balanced recommendations
    - Use "Advanced Options" for specific requirements
    - Add special notes for personalized planning
    
    **Trip History:**
    - Enable "Save trip history" in sidebar to keep your plans
    - Download trips as text files for offline access
    - Export before sharing with travel companions
    
    ### 🌍 Best Practices
    
    1. **Research visa requirements** well in advance
    2. **Check weather** for your travel dates
    3. **Book refundable** options when possible
    4. **Learn basic phrases** in local language
    5. **Respect local customs** and dress codes
    6. **Stay hydrated** and protect against sun/cold
    7. **Have backup plans** for activities
    8. **Keep valuables secure** and use hotel safes
    
    ### 📞 Emergency Contacts
    
    Always know:
    - Local emergency number (911, 112, etc.)
    - Your embassy/consulate contact
    - Your accommodation address and phone
    - Your travel insurance helpline
    
    ### 🤝 Providing Feedback
    
    TripGenie is an educational project and we value your feedback!
    - Use the sidebar settings for customization
    - Report issues or suggest features
    - Share your successful trips with us
    """)

# =============================
#   FOOTER
# =============================
st.markdown("---")
st.caption(f"🌍 TripGenie v{settings.version} • Educational AI Travel Assistant • Built with LangGraph + Streamlit")
st.caption("⚠️ **Disclaimer:** TripGenie is an educational project. Always verify prices, availability, and travel requirements before booking.")
st.caption("Made with ❤️ for travelers worldwide")

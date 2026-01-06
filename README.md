# TripGenie - AI Travel Planner 🌍

An intelligent, transparent, and educational AI travel planner powered by LangGraph and real-time search.

## ✨ Features

- 🤖 **AI-Powered Planning**: Uses LangGraph with Llama-3.3-70b for intelligent itinerary generation
- 🔍 **Real-Time Search**: Integrates Tavily and DuckDuckGo for current travel information
- 🗺️ **Smart Location Search**: OpenStreetMap integration for accurate location finding
- 💾 **Trip History**: Save and manage your trip plans
- 📥 **Export Options**: Download plans as formatted text files
- 🎯 **Customizable**: Detailed preferences for budget, style, food, and pace
- 📊 **Transparent**: Always cites sources for recommendations
- 🔒 **Safe & Validated**: Input validation and error handling throughout

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- API Keys:
  - [Groq API Key](https://console.groq.com/) (for LLM)
  - [Tavily API Key](https://tavily.com/) (for search)

### Installation

1. **Clone or download the repository**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup environment variables**

Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

4. **Run the application**
```bash
streamlit run ui/app.py
```

The app will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
Trip_planner/
│
├── config/              # Configuration and settings
│   ├── settings.py     # App configuration
│   └── prompts.py      # System prompts
│
├── services/           # Core services
│   ├── agent_service.py       # LangGraph agent
│   ├── location_service.py    # Location search
│   └── storage_service.py     # Trip history storage
│
├── utils/              # Utilities
│   ├── logger.py       # Logging configuration
│   ├── validators.py   # Input validation
│   └── formatters.py   # Output formatting
│
├── ui/                 # User interface
│   └── app.py          # Streamlit app
│
├── data/               # Data storage
│   └── trip_history.json
│
├── logs/               # Log files
│
├── main.py             # Entry point
├── requirements.txt    # Dependencies
└── README.md          # This file
```

## 🎯 How to Use

### 1. Plan a Trip

1. **Enter Locations**: Type your departure city and destination
2. **Set Details**: Choose number of travelers, trip duration, and group type
3. **Customize**: Select transport, budget, food preferences, and trip style
4. **Generate**: Click "Generate My Trip Plan" and wait for AI magic!
5. **Save/Export**: Download your plan or save it to history

### 2. View Trip History

- Access saved trips in the "Trip History" tab
- Download or delete individual trips
- Clear all history if needed

### 3. Tips & Guide

- Read travel planning tips
- Learn how to use TripGenie effectively
- Find safety and budget travel advice

## 🛠️ Configuration

### Customizing Settings

Edit `config/settings.py` to customize:

- **Model Settings**: Change LLM model, temperature, etc.
- **Search Settings**: Adjust search result limits
- **UI Settings**: Modify page layout and limits
- **Location Settings**: Configure location search parameters

### Environment Variables

Required:
- `GROQ_API_KEY`: Your Groq API key
- `TAVILY_API_KEY`: Your Tavily API key

Optional:
- `ENVIRONMENT`: Set to "production" for production mode
- `LANGCHAIN_TRACING_V2`: Enable LangSmith tracing (default: true)

## 📊 Features in Detail

### AI Agent

- Uses LangGraph for orchestrated AI workflows
- Llama-3.3-70b model for high-quality responses
- Tool calling for real-time information retrieval
- Transparent citation of sources

### Search Integration

- **Tavily**: Primary tool for travel-specific searches
- **DuckDuckGo**: Fallback for general queries
- Real-time flight and hotel price search
- Current travel advisories and tips

### Location Search

- OpenStreetMap Nominatim API
- Rate-limited and respectful API usage
- Detailed location information
- Coordinates for future map integration

### Input Validation

- Comprehensive input validation
- Sanitization of user inputs
- Clear error messages
- Protection against invalid data

### Logging

- Detailed logging to files and console
- User action tracking
- API call monitoring
- Error tracking with stack traces

## 🔧 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### Code Quality

```bash
# Format code
black .

# Check types
mypy .

# Lint
flake8 .
```

## 🚧 Roadmap

### Phase 1: Core Enhancements ✅
- [x] Fix critical bugs
- [x] Add input validation
- [x] Implement logging
- [x] Add trip history

### Phase 2: User Experience 🔄
- [ ] Interactive maps (Folium)
- [ ] Real-time price tracking
- [ ] Weather integration
- [ ] Budget calculator

### Phase 3: Advanced Features 📅
- [ ] User authentication
- [ ] Collaboration features
- [ ] Smart recommendations
- [ ] Booking integration

### Phase 4: Polish 🎨
- [ ] Multi-language support
- [ ] Photo galleries
- [ ] Gamification
- [ ] Analytics dashboard

## 🤝 Contributing

This is an educational project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is for educational purposes. Please check with the original author for licensing details.

## ⚠️ Disclaimer

TripGenie is an educational AI travel planner. Always verify:
- Flight prices and availability
- Hotel rates and booking terms
- Visa and travel requirements
- Safety advisories
- Local laws and customs

This tool provides recommendations but does not handle actual bookings.

## 📧 Support

For issues, questions, or suggestions:
- Check the logs in `logs/` directory
- Enable debug mode in sidebar settings
- Review error messages carefully
- Ensure API keys are correctly set

## 🙏 Acknowledgments

- **LangChain & LangGraph**: For the AI orchestration framework
- **Groq**: For fast LLM inference
- **Tavily**: For real-time search capabilities
- **OpenStreetMap**: For location data
- **Streamlit**: For the beautiful UI framework

---

Made with ❤️ for travelers worldwide

**Version**: 1.0.0
**Last Updated**: January 2025

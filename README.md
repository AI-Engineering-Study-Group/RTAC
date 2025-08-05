# 🎤 RTAC - "répondrai toujours avec certitude"

**RTAC** (French for "will always respond with certainty") is a play on words responding to RSVP - a plug-and-play AI assistant platform for event organizers. Bring your event details, and RTAC spins up a custom AI chat that answers questions about your event.

## 🌟 What is RTAC?

RTAC is a comprehensive AI assistant platform that transforms any event into an intelligent, conversational experience. Whether you're organizing a conference, workshop, meetup, or any gathering, RTAC provides:

- **🤖 Custom AI Assistant**: Personalized AI that knows your event inside and out
- **📅 Event Management**: Schedule, speakers, sessions, and venue information
- **🧭 Navigation & Logistics**: Directions, transportation, and venue details
- **💬 Interactive Support**: Real-time answers to attendee questions
- **🌐 Web Integration**: Dynamic data fetching from your event website
- **📱 Modern UI**: Beautiful, responsive chat interface

## 🚀 Quick Start

### Prerequisites

- Python 3.13 or higher
- Node.js 18+ (for frontend)
- Poetry (for Python dependency management)
- Docker & Docker Compose (recommended)
- Google API Key (for Google ADK and Maps)

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd RTAC
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys and event configuration
   ```

3. **Add your event data**
   ```bash
   # Place your event CSV files in the data/ directory
   # Update speakers.json with your speaker information
   ```

4. **Build and run with Docker**
   ```bash
   docker-compose up --build
   ```

5. **Access your event AI assistant**
   - **Frontend**: http://localhost
   - **API Docs**: http://localhost/docs
   - **Health Check**: http://localhost/api/v1/agents/health

### Option 2: Local Development

1. **Clone and set up backend**
   ```bash
   git clone <repository-url>
   cd RTAC
   cp env.example .env
   poetry install
   ```

2. **Set up frontend**
   ```bash
   cd frontend
   npm install
   ```

3. **Configure your event**
   ```bash
   # In your .env file:
   GOOGLE_API_KEY=your_google_api_key_here
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
   CONFERENCE_VENUE_NAME=Your Event Venue
   CONFERENCE_VENUE_ADDRESS=Your Venue Address
   CONFERENCE_VENUE_COORDINATES=lat,lng
   CONFERENCE_DATES=Your Event Dates
   SUPPORT_PHONE=Your Support Phone
   SUPPORT_EMAIL=Your Support Email
   ```

4. **Run the applications**
   ```bash
   # Terminal 1 - Backend
   poetry run python main.py
   
   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

## 🏗️ Architecture

```
RTAC/
├── app/
│   ├── agents/
│   │   ├── apiconf_agent.py          # Main AI agent implementation
│   │   └── tools/
│   │       ├── navigation_tools.py   # Maps, directions, transportation
│   │       ├── speaker_tools.py      # Speaker information
│   │       ├── schedule_tools.py     # Event scheduling
│   │       ├── organizer_tools.py    # Event organization
│   │       ├── calendar_tools.py     # Calendar integration
│   │       ├── csv_schedule_tools.py # CSV data processing
│   │       └── web_scraping_tools.py # Data extraction from websites
│   ├── config/
│   │   ├── settings.py               # Environment configuration
│   │   └── logger.py                 # Logging setup
│   ├── schemas/
│   │   ├── base.py                   # Base response schemas
│   │   └── agents.py                 # Agent request/response models
│   ├── services/
│   │   ├── agent_config.py          # Agent configuration
│   │   ├── agent_factory.py         # Agent creation
│   │   ├── message_processor.py     # Message handling
│   │   ├── response_formatter.py    # Response formatting
│   │   ├── response_processor.py    # Response processing
│   │   ├── session_manager.py       # Session management
│   │   ├── tool_manager.py          # Tool management
│   │   └── web_scraping_service.py  # Web scraping functionality
│   └── api/
│       └── v1/
│           └── agents_router.py      # FastAPI endpoints
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat.tsx              # Chat interface
│   │   │   ├── Sidebar.tsx           # Navigation sidebar
│   │   │   └── TypingIndicator.tsx   # Loading animations
│   │   ├── App.tsx                   # Main React app
│   │   └── main.tsx                  # React entry point
│   ├── package.json                  # Frontend dependencies
│   └── vite.config.ts                # Vite configuration
├── data/
│   ├── speakers.json                 # Speaker information
│   └── *.csv                        # Event schedule and data
├── docker/
│   ├── Dockerfile                    # Backend container
│   └── nginx/
│       ├── Dockerfile                # Nginx container
│       └── nginx.conf                # Nginx configuration
├── scripts/
│   ├── update_csv_data.py           # Data update automation
│   └── run_csv_update.sh            # Update script runner
├── pyproject.toml                    # Python dependencies
├── docker-compose.yml                # Container orchestration
├── env.example                       # Environment variables template
├── main.py                           # FastAPI application entry
└── README.md                         # This file
```

## 📚 API Documentation

### Endpoints

#### Chat with Event AI Assistant
```http
POST /api/v1/agents/chat
```

**Request Body:**
```json
{
  "message": "What sessions are happening today?",
  "user_id": "user123",
  "session_id": "session456"
}
```

**Response:**
```json
{
  "success": true,
  "response": "Here are today's sessions...",
  "user_id": "user123",
  "session_id": "session456",
  "confidence": 0.9,
  "metadata": {
    "user_id": "user123",
    "session_id": "session456",
    "timestamp": 1703123456.789,
    "tools_used": []
  }
}
```

#### Get Agent Status
```http
GET /api/v1/agents/status
```

#### Health Check
```http
GET /api/v1/agents/health
```

### Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost/docs
- **ReDoc**: http://localhost/redoc

## 🛠️ Development

### Project Structure

The project follows a modular architecture:

- **`app/agents/`**: AI agent implementation and tools
- **`app/config/`**: Configuration and settings management
- **`app/schemas/`**: Pydantic models for API requests/responses
- **`app/api/`**: FastAPI routes and endpoints
- **`app/services/`**: Business logic and external service integrations
- **`frontend/`**: React application with TypeScript
- **`data/`**: Static data files (speakers, schedule)

### Adding New Tools

1. Create a new tool file in `app/agents/tools/`
2. Implement your tool functions following Google ADK conventions
3. Register the tool in `app/agents/apiconf_agent.py`
4. Update the agent instructions if needed

Example tool:
```python
# app/agents/tools/my_tool.py
from google.adk.tools import FunctionTool

def my_tool_function(param: str, **kwargs) -> Dict[str, Any]:
    """My custom tool function."""
    return {
        "success": True,
        "result": f"Processed: {param}"
    }

def get_my_tools() -> List[FunctionTool]:
    """Get my custom tools."""
    return [
        FunctionTool(
            name="my_tool",
            description="A custom tool for processing data",
            function=my_tool_function
        )
    ]
```

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GOOGLE_API_KEY` | Google ADK API key | Yes | - |
| `GOOGLE_MODEL_NAME` | Google model to use | No | gemini-2.5-flash |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key | Yes | - |
| `DATABASE_URL` | PostgreSQL database URL | Yes | - |
| `REDIS_URL` | Redis connection URL | No | redis://localhost:6379/0 |
| `CONFERENCE_VENUE_NAME` | Event venue name | Yes | - |
| `CONFERENCE_VENUE_ADDRESS` | Venue address | Yes | - |
| `CONFERENCE_VENUE_COORDINATES` | Venue coordinates (lat,lng) | Yes | - |
| `CONFERENCE_DATES` | Event dates | Yes | - |
| `SUPPORT_PHONE` | Support phone number | Yes | - |
| `SUPPORT_EMAIL` | Support email | Yes | - |
| `SECRET_KEY` | Application secret key | Yes | - |
| `CORS_ORIGINS` | Allowed CORS origins | No | ["http://localhost:3000"] |

## 🧪 Testing

### Run Tests
```bash
poetry run pytest
```

### Run with Coverage
```bash
poetry run pytest --cov=app
```

### Frontend Testing
```bash
cd frontend
npm run lint
```

## 🚀 Deployment

### Docker Deployment

1. **Build production images**
   ```bash
   docker-compose -f docker-compose.yml build
   ```

2. **Run in production mode**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

### Environment Configuration

For production deployment, ensure you have:

- **Database**: PostgreSQL instance
- **Redis**: Redis instance for caching
- **API Keys**: Valid Google ADK and Maps API keys
- **SSL**: HTTPS certificates for production
- **Domain**: Configured domain name

## 📊 Monitoring

The application includes comprehensive logging and monitoring:

- **Structured Logging**: All operations are logged with context
- **Health Checks**: Built-in health check endpoints
- **Performance Metrics**: Request processing time headers
- **Error Handling**: Graceful error handling with fallback options
- **Session Management**: Conversation context tracking

## 🔧 Configuration

### Logging Levels
- `DEBUG`: Detailed debug information
- `INFO`: General information (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages

### CORS Configuration
Configure allowed origins in your `.env` file:
```bash
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

### Code Style

- **Python**: Follow PEP 8, use Black for formatting
- **TypeScript**: Use ESLint and Prettier
- **Google ADK**: Follow Google ADK conventions for agent development

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- **Phone**: Check your `.env` file for the support phone number
- **Email**: Check your `.env` file for the support email
- **Documentation**: Visit `/docs` when the server is running
- **AI Assistant**: Chat with your event AI directly through the application

## 🎯 Roadmap

- [ ] No-code event configuration interface
- [ ] Drag-and-drop tool builder
- [ ] Multi-language support
- [ ] Mobile app integration
- [ ] Advanced analytics and insights
- [ ] Integration with social media platforms
- [ ] Voice interface
- [ ] Offline mode for basic functionality
- [ ] Event template marketplace
- [ ] Real-time collaboration features

---

**Built with ❤️ for event organizers worldwide**

*RTAC - Making every event intelligent and interactive! 🎤✨* 
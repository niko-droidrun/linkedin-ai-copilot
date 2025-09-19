# LinkedIn AI Copilot

A FastAPI-based LinkedIn Profile Scraper REST Server that provides intelligent profile scraping with RAMS (Redis Agent Memory System) caching and BrightData fallback.

## Features

- 🚀 **Smart Scraping Strategy**: RAMS-first approach with BrightData fallback
- 💾 **Intelligent Caching**: Stores profile data and activities in RAMS for fast retrieval
- 🔄 **Automatic Fallback**: Falls back to BrightData API when cached data is unavailable
- 📊 **Activity Tracking**: Captures and stores recent LinkedIn activities
- 🌐 **REST API**: Clean HTTP endpoints for easy integration
- ⚡ **Fast Response**: Cached profiles return instantly

## Installation

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Access to RAMS (Redis Agent Memory System)
- BrightData API credentials

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd linkedin-ai-copilot
   ```

2. **Initialize the project with uv**
   ```bash
   uv init --name linkedin-ai-copilot
   ```

3. **Install dependencies**
   ```bash
   uv add fastapi pydantic python-dotenv requests uvicorn agent-memory-client
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root:
   ```env
   MEMORY_SERVER_URL=http://localhost:8000
   # Add other environment variables as needed
   ```

5. **Start the server**
   ```bash
   uv run python linkedin_scraper_server.py
   ```

   Or if port 8001 is already in use:
   ```bash
   uv run python -c "
   import uvicorn
   import sys
   sys.path.insert(0, '.')
   from linkedin_scraper_server import app
   uvicorn.run(app, host='0.0.0.0', port=8002, log_level='info')
   "
   ```

## API Endpoints

### Base URL
- Default: `http://localhost:8001`
- Alternative: `http://localhost:8002` (if port 8001 is in use)

### Available Endpoints

#### 1. Root Information
```http
GET /
```
Returns API information and available endpoints.

#### 2. Health Check
```http
GET /health
```
Checks server health and RAMS connection status.

#### 3. Scrape Profile (POST)
```http
POST /scrape
Content-Type: application/json

{
  "url": "https://www.linkedin.com/in/username/",
  "user_id": "api_user"
}
```

#### 4. Scrape Profile by Username (GET)
```http
GET /scrape/{username}?user_id=api_user
```

### Example Usage

**Scrape a LinkedIn profile:**
```bash
curl -X GET "http://localhost:8002/scrape/niels-schmidt-890b96303" \
     -H "accept: application/json"
```

**Response format:**
```json
{
  "success": true,
  "profile_data": {
    "id": "username",
    "name": "Full Name",
    "city": "City, State, Country",
    "followers": 123,
    "connections": 456,
    "current_company": {...},
    "activity_summary": "User has X recent activities: Y liked, Z commented."
  },
  "formatted_output": "...",
  "cached": false,
  "error": null
}
```

## Architecture

### RAMS-First Strategy
1. **Check RAMS**: Search for cached profile data
2. **BrightData Fallback**: If no cache found, scrape from BrightData API
3. **Store Results**: Cache new data in RAMS for future requests
4. **Activity Processing**: Store individual activities as separate memories

### Dependencies
- **FastAPI**: Web framework for REST API
- **Pydantic**: Data validation and serialization
- **python-dotenv**: Environment variable management
- **requests**: HTTP client for BrightData API
- **uvicorn**: ASGI server
- **agent-memory-client**: RAMS integration

## Development

### Project Structure
```
linkedin-ai-copilot/
├── linkedin_scraper_server.py  # Main server application
├── pyproject.toml             # Project configuration
├── README.md                  # This file
├── .env                       # Environment variables (create this)
└── .venv/                     # Virtual environment (auto-created)
```

### Running in Development
```bash
# Activate virtual environment
source .venv/bin/activate

# Run server directly
python linkedin_scraper_server.py

# Or with custom port
uvicorn linkedin_scraper_server:app --host 0.0.0.0 --port 8002 --reload
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MEMORY_SERVER_URL` | RAMS server URL | `http://localhost:8000` |

## License

[Add your license information here]

## Contributing

[Add contributing guidelines here]

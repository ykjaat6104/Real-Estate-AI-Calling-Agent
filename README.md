# Real Estate AI Calling Agent — Production

A **production-ready, multi-tenant SaaS platform** for AI-powered real estate voice calling agents.

## Features

- **Bilingual Support**: Hindi, English, and Hinglish conversations
- **Multi-Tenant**: Isolated data per organization/company
- **JWT Authentication**: Secure login with role-based access
- **Phone Calling**: Real PSTN calls via LiveKit SIP + Twilio
- **Call Analytics**: Sentiment analysis and lead scoring
- **CRM Integration**: Webhook system for external CRM sync
- **Real-Time Dashboard**: Live lead tracking and analytics
- **Docker Deployment**: Containerized for any cloud

## Tech Stack

| Component | Technology |
|-----------|------------|
| Voice/Media | LiveKit Agents (Python) |
| LLM | Groq Llama-3.3-70b |
| STT | Deepgram Nova-3 |
| TTS | ElevenLabs Multilingual |
| Database | Supabase (PostgreSQL) |
| Cache | Redis |
| Backend | FastAPI + Uvicorn |
| Auth | JWT + bcrypt |
| Frontend | Vanilla HTML/CSS/JS |
| Deployment | Docker + nginx |

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Supabase account (free tier)
- API keys: Groq, Deepgram, ElevenLabs, LiveKit

### Local Development

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd real-estate-ai-agent

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# 6. Run the application
uvicorn app.api:app --reload
```

### Production (Docker)

```bash
# 1. Set up environment
cp .env.example .env
# Edit .env with production credentials

# 2. Start all services
docker-compose up -d

# 3. Access the application
# Frontend: http://localhost
# API: http://localhost/api/v1
# Health: http://localhost/health
```

## Project Structure

```
real-estate-ai-agent/
├── app/                    # Main application
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic schemas
│   ├── api/                # API endpoints
│   ├── services/           # Business logic
│   ├── core/               # Security, rate limiting
│   ├── agent/              # LiveKit agent
│   └── web/                # Frontend
├── agent/                  # Original agent (reference)
├── backup/                 # Original files backup
├── tests/                  # Test suite
├── docs/                   # Documentation
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
└── requirements.txt
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Leads
- `POST /api/v1/leads/` - Create lead
- `GET /api/v1/leads/` - List leads
- `GET /api/v1/leads/{id}` - Get lead
- `PUT /api/v1/leads/{id}` - Update lead

### Health
- `GET /health` - Health check

## Configuration

All configuration is managed through environment variables. See `.env.example` for the complete list.

Key settings:
- `DATABASE_URL` - Supabase PostgreSQL connection
- `REDIS_URL` - Redis connection
- `LIVEKIT_URL/API_KEY/API_SECRET` - LiveKit credentials
- `GROQ_API_KEY` - Groq API key
- `DEEPGRAM_API_KEY` - Deepgram API key
- `ELEVENLABS_API_KEY` - ElevenLabs API key
- `SECRET_KEY` - JWT signing key

## Free Tier Tools

| Service | Tool | Free Tier |
|---------|------|-----------|
| LLM | Groq | 30 RPM, 10K tokens/min |
| STT | Deepgram | $200 credits |
| TTS | ElevenLabs | 10K chars/month |
| Voice | LiveKit Cloud | 10 audio-hours/month |
| Database | Supabase | 500MB, 50K MAU |
| Cache | Redis (self-hosted) | Unlimited |

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
ruff check .
```

### Database Migrations
```bash
alembic upgrade head
alembic revision --autogenerate -m "description"
```

## Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions.

## Documentation

- [implementation.md](implementation.md) - Complete implementation plan
- [PROJECT_STATE.md](PROJECT_STATE.md) - Progress tracker
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Deployment guide
- [docs/API.md](docs/API.md) - API documentation

## License

This project is licensed under the MIT License.

---

*Built with LiveKit, Groq, Deepgram, ElevenLabs, and FastAPI*

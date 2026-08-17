# Implementation Plan — Production Real Estate AI Calling Agent

> Multi-tenant SaaS platform with phone calling, analytics, and CRM integration.
> Tech stack: LiveKit Agents + Groq + Deepgram + ElevenLabs + Supabase + Redis + Docker

---

## 1. Project Overview

### Goal
Transform the prototype real estate AI calling agent into a production-ready, multi-tenant SaaS platform that supports:
- Bilingual conversations (Hindi, English, Hinglish)
- Real phone calling via LiveKit SIP
- Call analytics and sentiment analysis
- CRM webhook integration
- JWT authentication with tenant isolation
- Docker deployment

### Tech Stack
| Component | Technology | Why |
|-----------|------------|-----|
| Voice/Media | LiveKit Agents (Python) | Open-source, handles WebRTC, echo cancellation, turn detection |
| LLM | Groq Llama-3.3-70b | Fast (600+ tok/s), free tier, function-calling |
| STT | Deepgram Nova-3 | Best Indian-accent + Hinglish robustness |
| TTS | ElevenLabs multilingual | One voice speaks Hindi/Hinglish/English naturally |
| Database | Supabase (PostgreSQL) | Managed PostgreSQL with auth and real-time |
| Cache | Redis | Rate limiting, sessions, caching |
| Backend | FastAPI + Uvicorn | Lightweight, async, auto-docs |
| Auth | JWT + bcrypt | Stateless, scalable |
| Frontend | Vanilla HTML/CSS/JS | Simple, no build step |
| Deployment | Docker + nginx | Containerized, production-ready |

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        NGINX (Reverse Proxy)                     │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
│   Web Backend      │ │   Agent Worker     │ │   Phone Gateway    │
│   (FastAPI)        │ │   (LiveKit Agents) │ │   (LiveKit SIP)    │
│                    │ │                    │ │                    │
│  - Auth/JWT        │ │  - Voice cascade   │ │  - Inbound calls   │
│  - Lead APIs       │ │  - Multi-tenant    │ │  - Outbound calls  │
│  - Analytics       │ │  - Sentiment       │ │  - Call routing    │
│  - CRM webhooks    │ │  - Call recording  │ │                    │
│  - Static frontend │ │  - Analytics emit  │ │                    │
└─────────┬──────────┘ └─────────┬──────────┘ └─────────┬──────────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Supabase   │  │    Redis     │  │  LiveKit     │          │
│  │ (PostgreSQL) │  │ (Rate limit) │  │   Cloud      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. File Structure

```
real-estate-ai-agent/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── config.py                 # Pydantic settings
│   ├── models/                   # SQLAlchemy models
│   │   ├── base.py
│   │   ├── tenant.py
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── lead.py
│   │   ├── call.py
│   │   └── webhook.py
│   ├── schemas/                  # Pydantic request/response
│   │   ├── auth.py
│   │   ├── project.py
│   │   └── lead.py
│   ├── api/                      # FastAPI routers
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       └── leads.py
│   ├── services/                 # Business logic
│   │   ├── auth.py
│   │   └── lead.py
│   ├── core/                     # Shared utilities
│   │   ├── __init__.py
│   │   ├── security.py
│   │   └── rate_limit.py
│   ├── agent/                    # LiveKit agent
│   │   ├── __init__.py
│   │   ├── prompt_factory.py
│   │   ├── pipeline.py
│   │   └── tools.py
│   └── web/                      # Frontend
│       ├── index.html
│       ├── login.html
│       ├── dashboard.html
│       ├── css/style.css
│       └── js/
│           ├── app.js
│           ├── auth.js
│           └── dashboard.js
├── agent/                        # Legacy agent (kept for reference)
│   ├── config.py
│   ├── persona.py
│   ├── project_data.py
│   └── schemas.py
├── backup/                       # Backup of original files
├── tests/                        # Test suite
├── docs/                         # Documentation
├── alembic/                      # Database migrations
├── .env.example                  # Environment template
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── README.md
├── implementation.md             # This file
└── PROJECT_STATE.md              # Progress tracker
```

---

## 4. Database Schema

### Tables
1. **tenants** - Organizations using the platform
2. **users** - Users within tenants (with roles)
3. **projects** - Real estate projects
4. **leads** - Captured sales leads
5. **call_records** - Call analytics and recordings
6. **webhooks** - CRM integration endpoints
7. **webhook_deliveries** - Webhook delivery logs

### Row Level Security (RLS)
- Each table has tenant_id foreign key
- RLS policies ensure users only see their tenant's data
- Automatic tenant isolation at database level

---

## 5. API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Leads
- `POST /api/v1/leads/` - Create lead
- `GET /api/v1/leads/` - List leads
- `GET /api/v1/leads/{id}` - Get lead
- `PUT /api/v1/leads/{id}` - Update lead
- `GET /api/v1/leads/call/{call_id}` - Get lead by call ID

### Projects (to be implemented)
- `POST /api/v1/projects/` - Create project
- `GET /api/v1/projects/` - List projects
- `GET /api/v1/projects/{id}` - Get project
- `PUT /api/v1/projects/{id}` - Update project

### Phone (to be implemented)
- `POST /api/v1/phone/call/outbound` - Initiate outbound call
- `GET /api/v1/phone/calls/active` - Get active calls

### Webhooks (to be implemented)
- `POST /api/v1/webhooks/` - Create webhook
- `GET /api/v1/webhooks/` - List webhooks
- `POST /api/v1/webhooks/{id}/test` - Test webhook

---

## 6. Implementation Phases

### Phase 1: Foundation (Days 1-3)
- [x] Clean up old files
- [x] Create new project structure
- [x] Set up Pydantic settings
- [x] Create database models
- [x] Set up Docker configuration

### Phase 2: Auth & Multi-Tenancy (Days 3-5)
- [x] Implement JWT authentication
- [x] Create auth API endpoints
- [x] Add rate limiting with Redis
- [x] Set up tenant isolation

### Phase 3: Enhanced Agent (Days 5-7)
- [x] Create bilingual prompt factory
- [x] Set up STT/LLM/TTS pipeline
- [x] Create function tools
- [ ] Add sentiment analysis
- [ ] Add lead scoring

### Phase 4: API & Frontend (Days 7-10)
- [x] Create lead API endpoints
- [x] Create frontend pages
- [x] Add authentication UI
- [x] Enhance dashboard with analytics

### Phase 5: Phone Calling (Days 10-12)
- [ ] Set up LiveKit SIP
- [ ] Configure Twilio integration
- [ ] Create phone APIs
- [ ] Add call recording

### Phase 6: Webhooks & Analytics (Days 12-13)
- [ ] Create webhook system
- [ ] Add event dispatch
- [ ] Create delivery logging

### Phase 7: Deployment (Days 13-14)
- [ ] Set up nginx
- [ ] Create CI/CD pipeline
- [ ] Add health checks
- [ ] Write documentation

---

## 7. Configuration

All configuration is managed through environment variables. See `.env.example` for the complete list.

Key settings:
- `DATABASE_URL` - Supabase PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `LIVEKIT_URL/API_KEY/API_SECRET` - LiveKit Cloud credentials
- `GROQ_API_KEY` - Groq API key for LLM
- `DEEPGRAM_API_KEY` - Deepgram API key for STT
- `ELEVENLABS_API_KEY` - ElevenLabs API key for TTS
- `SECRET_KEY` - JWT signing key

---

## 8. Deployment

### Local Development
```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment file
cp .env.example .env
# Edit .env with your credentials

# 4. Start services
docker-compose up -d redis
uvicorn app.api:app --reload
```

### Production (Docker)
```bash
# 1. Build and start all services
docker-compose -f docker-compose.yml up -d

# 2. Or with production overrides
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 9. Free Tier Tools

| Service | Tool | Free Tier |
|---------|------|-----------|
| LLM | Groq | 30 RPM, 10K tokens/min |
| STT | Deepgram | $200 credits |
| TTS | ElevenLabs | 10K chars/month |
| Voice | LiveKit Cloud | 10 audio-hours/month |
| Database | Supabase | 500MB, 50K MAU |
| Cache | Redis (self-hosted) | Unlimited |

---

## 10. Next Steps

1. **Complete Phase 3** - Add sentiment analysis and lead scoring
2. **Complete Phase 5** - Set up phone calling
3. **Complete Phase 6** - Add webhook system
4. **Complete Phase 7** - Finalize deployment
5. **Write tests** - Add unit and integration tests
6. **Documentation** - Complete API docs and user guide

---

## 11. Original Files (Preserved)

The following files from the original prototype are preserved in `agent/` and `backup/`:
- `agent/persona.py` - Original conversation flow
- `agent/project_data.py` - Dummy project data
- `agent/schemas.py` - Original lead schema
- `backup/` - Complete backup of original files

These are kept for reference and can be used to populate the database with sample data.

---

*Last updated: August 2024*

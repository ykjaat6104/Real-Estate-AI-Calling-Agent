"""Pydantic settings for the Real Estate AI Calling Agent."""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "Real Estate AI Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str  # For JWT signing

    # Supabase / PostgreSQL
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    DATABASE_URL: str  # postgresql+asyncpg://...

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # LiveKit (media server / WebRTC)
    LIVEKIT_URL: str
    LIVEKIT_API_KEY: str
    LIVEKIT_API_SECRET: str

    # Groq (LLM brain)
    GROQ_API_KEY: str
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE: float = 0.7

    # Deepgram (STT)
    DEEPGRAM_API_KEY: str = ""
    STT_PROVIDER: str = "deepgram"  # deepgram | groq
    STT_MODEL: str = "nova-3"
    STT_LANGUAGE: str = "hi"  # hi | en | en-IN | auto

    # ElevenLabs (TTS)
    ELEVENLABS_API_KEY: str = ""
    TTS_MODEL: str = "eleven_multilingual_v2"
    TTS_VOICE_ID: str = ""

    # JWT Auth
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 60
    JWT_REFRESH_EXPIRY_DAYS: int = 7

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_TENANT_PER_HOUR: int = 1000

    # Twilio (Phone - optional)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # Storage
    RECORDINGS_PATH: str = "./recordings"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()

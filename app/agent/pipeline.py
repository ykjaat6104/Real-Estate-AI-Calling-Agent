"""STT/LLM/TTS pipeline factory."""
from livekit.plugins import deepgram, elevenlabs, openai, silero

from app.config import get_settings

settings = get_settings()


def make_stt():
    """Create Speech-to-Text provider based on configuration."""
    if settings.STT_PROVIDER == "groq":
        return openai.STT(
            model=settings.STT_MODEL,
            language=settings.STT_LANGUAGE,
            base_url=settings.GROQ_BASE_URL,
            api_key=settings.GROQ_API_KEY,
        )
    return deepgram.STT(
        model=settings.STT_MODEL,
        language=settings.STT_LANGUAGE,
        detect_language=(settings.STT_LANGUAGE == "auto"),
        interim_results=True,
        api_key=settings.DEEPGRAM_API_KEY,
    )


def make_llm():
    """Create Language Model provider."""
    return openai.LLM(
        model=settings.LLM_MODEL,
        base_url=settings.GROQ_BASE_URL,
        api_key=settings.GROQ_API_KEY,
        temperature=settings.LLM_TEMPERATURE,
    )


def make_tts():
    """Create Text-to-Speech provider."""
    return elevenlabs.TTS(
        model=settings.TTS_MODEL,
        voice_id=settings.TTS_VOICE_ID,
        api_key=settings.ELEVENLABS_API_KEY,
    )


def make_vad():
    """Create Voice Activity Detection provider."""
    return silero.VAD.load()

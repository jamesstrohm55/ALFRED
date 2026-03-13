from dotenv import load_dotenv
import os

load_dotenv()

# API Keys
ELEVENLABS_KEY = os.getenv("XI_API_KEY")
ALFRED_VOICE_ID = os.getenv("XI_VOICE_ID")
OPENAI_KEY = os.getenv("OPENAI_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Voice Settings
VOICE_RATE = 100
VOICE_PITCH = 100
LANGUAGE = "en-uk"

# Paths
MUSIC_PATH = os.getenv("MUSIC_PATH", "")
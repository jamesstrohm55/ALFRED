import pyttsx3
from elevenlabs import ElevenLabs, play, VoiceSettings
from config import ELEVENLABS_KEY, ALFRED_VOICE_ID, VOICE_RATE

# Initialize ElevenLabs client
elevenlabs_client = None
if ELEVENLABS_KEY and ALFRED_VOICE_ID:
    elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_KEY)

# Initialize pyttsx3 as offline fallback
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', VOICE_RATE)


def speak_with_pyttsx3(text):
    """Offline TTS fallback using pyttsx3."""
    try:
        tts_engine.say(text)
        tts_engine.runAndWait()
        return True
    except Exception as e:
        print(f"[pyttsx3 error] {e}")
        return False


def speak(text):
    print(f"A.L.F.R.E.D: {text}")

    # Try ElevenLabs first (premium voice)
    if elevenlabs_client:
        try:
            audio = elevenlabs_client.text_to_speech.convert(
                text=text,
                voice_id=ALFRED_VOICE_ID,
                model_id="eleven_monolingual_v1",
                voice_settings=VoiceSettings(
                    stability=0.4,
                    similarity_boost=0.75
                )
            )
            play(audio)
            return
        except Exception as e:
            print(f"[ElevenLabs failed] {e}")

    # Fallback to pyttsx3 (offline)
    if speak_with_pyttsx3(text):
        return

    # Final fallback: text only
    print(f"A.L.F.R.E.D (text-only): {text}")

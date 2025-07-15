from elevenlabs import ElevenLabs, play, VoiceSettings
from config import ELEVENLABS_KEY, ALFRED_VOICE_ID

# Initialize ElevenLabs client
client = ElevenLabs(api_key=ELEVENLABS_KEY)

def speak(text):
    print(f"A.L.F.R.E.D: {text}")

    try:
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=ALFRED_VOICE_ID,
            model_id="eleven_monolingual_v1",  # Or eleven_multilingual_v2
            voice_settings=VoiceSettings(
                stability=0.4,
                similarity_boost=0.75
            )
        )
        play(audio)

    except Exception as e:
        print(f"[Fallback to text] Could not synthesize speech")
        print(f"A.L.F.R.E.D (text-only): {text}")

# A.L.F.R.E.D

> **All-Knowing Logical Facilitator for Reasoned Execution of Duties**

A.L.F.R.E.D is a modular, intelligent, and voice-enabled personal assistant inspired by J.A.R.V.I.S. Completely powered by Python, it integrates multiple AI technologies, APIs, and system commands to create a cohesive and interactive digital assistant for personal and professional productivity.

---

## Features

- **Voice Interaction**: Speech synthesis with ElevenLabs (text fallback if credits are exhausted)
- **LLM-Powered Conversations**: Multi-layered LLM fallback (OpenAI, OpenRouter, Claude)
- **Memory System**: Store, recall, forget, and list facts about the user with semantic search
- **System Monitoring**: Real-time CPU, RAM, Disk usage, uptime, and OS info
- **Weather Reports**: Get weather updates based on your current location
- **Calendar Management**: Integrate with Google Calendar to create and retrieve events
- **File Assistant**: Search, open, and delete files via voice/text commands
- **GUI Overlay**: Floating system monitor overlay
- **System Automation**: Lock system, open apps, play music, shutdown
- **Command Logging**: Logs all commands to `command_log.txt`
- **Text Fallback Mode**: Automatically switches to text if microphone is not detected

---

## Project Structure

```
ALFRED/
│
├── core/                        # Voice & brain logic
│   ├── __init__.py
│   ├── brain.py                 # Command routing & LLM integration
│   ├── listener.py              # Speech recognition
│   ├── personality.py           # Personality traits
│   └── voice.py                 # Text-to-speech (ElevenLabs)
│
├── memory/                      # Persistent memory system
│   └── memory_manager.py        # JSON-based memory storage
│
├── service_commands/            # Modular command handlers
│   ├── calendar_commands.py
│   ├── file_assistant_commands.py
│   ├── memory_commands.py
│   ├── system_monitor_commands.py
│   └── weather_commands.py
│
├── services/                    # System & external services
│   ├── automation.py            # System commands (browser, lock, etc.)
│   ├── calendar_service.py      # Google Calendar API
│   ├── embeddings_manager.py    # ChromaDB vector storage
│   ├── file_assistant.py        # File operations
│   ├── system_monitor.py        # System stats
│   └── weather_service.py       # OpenWeather API
│
├── ui/                          # GUI components
│   ├── gui.py
│   └── system_overlay.py
│
├── utils/                       # Utility functions
│   └── logger.py
│
├── data/                        # Data storage (gitignored)
│   ├── memory.json              # Persistent memory
│   └── embeddings_db/           # ChromaDB vector database
│
├── .env                         # Environment variables (gitignored)
├── config.py                    # Configuration loader
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/jamesstrohm55/ALFRED.git
cd ALFRED
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI
OPENAI_KEY=your_openai_api_key

# OpenRouter (fallback LLM)
OPENROUTER_API_KEY=your_openrouter_api_key

# ElevenLabs (voice synthesis)
XI_API_KEY=your_elevenlabs_api_key
XI_VOICE_ID=your_elevenlabs_voice_id

# OpenWeather
WEATHER_API_KEY=your_openweather_api_key
```

### 5. Set Up Google Calendar (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project and enable the Google Calendar API
3. Download `credentials.json` and place it in the project root
4. On first run, you'll be prompted to authorize access

### 6. Run Application

```bash
python main.py
```

---

## Usage Examples

| Command | Description |
|---------|-------------|
| "What is the weather today?" | Get current weather |
| "Remember that my favorite color is blue" | Store a fact |
| "What do you remember about my favorite color?" | Recall a fact |
| "Forget my favorite color" | Delete a fact |
| "What do you remember?" | List all stored facts |
| "Tell time" | Get current time |
| "Open browser" | Open default browser |
| "Open VS Code" | Launch VS Code |
| "Lock computer" | Lock workstation |
| "What's on my calendar?" | List upcoming events |
| "Create an event" | Add calendar event |
| "Find resume" | Search for files |
| "System status" | Get CPU/RAM/Disk stats |

If no microphone is detected, the system prompts for text input.

---

## Roadmap

- [ ] Browser-based dashboard
- [ ] Email integration
- [ ] Smart notification system
- [ ] Advanced file manager with suggestions
- [ ] Auto-pilot mode with multi-step reasoning
- [ ] Emotional recognition and response adaptation
- [ ] Conversation context (multi-turn conversations)
- [ ] Offline TTS fallback (pyttsx3)

---

## Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/feature-name`
3. Commit your changes: `git commit -m 'Add new feature'`
4. Push to the branch: `git push origin feature/feature-name`
5. Open a Pull Request

---

## License

This project is licensed under the MIT License. See LICENSE for more information.

---

## Credits

Developed by James Strohm.

Inspired by the vision of AI assistants like J.A.R.V.I.S and powered by modern LLMs, APIs, and system tools.

> "I am A.L.F.R.E.D, your logical facilitator. How may I assist you today?"

# A.L.F.R.E.D

> **All-Knowing Logical Facilitator for Reasoned Execution of Duties**

A.L.F.R.E.D is a modular, intelligent, and voice-enabled personal assistant inspired by J.A.R.V.I.S. Completely powered by Python, it integrates multiple AI technologies, APIs, and system commands to create a cohesive and interactive digital assistant for personal and professional productivity.

---

## Features

### Core Capabilities
- **Voice Interaction**: Speech recognition and synthesis with ElevenLabs (pyttsx3 offline fallback)
- **LLM-Powered Conversations**: Multi-layered LLM fallback (OpenAI, OpenRouter, Claude)
- **Memory System**: Store, recall, forget, and list facts with semantic search (ChromaDB)
- **System Monitoring**: Real-time CPU, RAM, Disk usage, uptime, and OS info
- **Weather Reports**: Get weather updates based on your location
- **Calendar Management**: Google Calendar integration for events
- **File Assistant**: Search, open, and delete files via voice/text
- **System Automation**: Lock system, open apps, play music, shutdown

### Modern GUI (PySide6)
- **Chat Interface**: Modern chat bubbles with timestamps
- **Voice Waveform Visualizer**: Real-time audio visualization for input/output
- **Quick Action Tiles**: One-click buttons for common commands
- **System Dashboard**: Live charts for CPU, RAM, and Disk with 60-second history
- **Dark Theme**: JARVIS-inspired cyan/dark aesthetic

---

## Project Structure

```
ALFRED/
│
├── core/                           # Voice & brain logic
│   ├── brain.py                    # Command routing & LLM integration
│   ├── listener.py                 # Speech recognition
│   ├── personality.py              # Personality traits
│   └── voice.py                    # Text-to-speech (ElevenLabs + pyttsx3)
│
├── memory/                         # Persistent memory system
│   └── memory_manager.py           # JSON + ChromaDB storage
│
├── service_commands/               # Modular command handlers
│   ├── calendar_commands.py
│   ├── file_assistant_commands.py
│   ├── memory_commands.py
│   ├── system_monitor_commands.py
│   └── weather_commands.py
│
├── services/                       # System & external services
│   ├── automation.py               # System commands
│   ├── calendar_service.py         # Google Calendar API
│   ├── embeddings_manager.py       # ChromaDB vector storage
│   ├── file_assistant.py           # File operations
│   ├── system_monitor.py           # System stats
│   └── weather_service.py          # OpenWeather API
│
├── ui/                             # GUI components (PySide6)
│   ├── app.py                      # Application entry point
│   ├── main_window.py              # Main window
│   ├── signals.py                  # Global Qt signals
│   ├── widgets/                    # UI widgets
│   │   ├── chat_widget.py          # Chat bubbles
│   │   ├── waveform_widget.py      # Audio visualizer
│   │   ├── quick_actions.py        # Action tiles
│   │   ├── system_dashboard.py     # System charts
│   │   └── input_bar.py            # Text/voice input
│   ├── threads/                    # Background workers
│   │   ├── audio_thread.py         # Microphone capture
│   │   ├── command_worker.py       # Command processing
│   │   └── system_monitor_thread.py
│   └── styles/                     # Theming
│       ├── colors.py               # Color palette
│       └── dark_theme.py           # QSS stylesheet
│
├── utils/                          # Utility modules
│   └── logger.py                   # Centralized logging system
│
├── data/                           # Data storage (gitignored)
│   ├── memory.json                 # Persistent memory
│   └── embeddings_db/              # ChromaDB database
│
├── logs/                           # Application logs (auto-created)
│   └── alfred_YYYYMMDD.log         # Daily log files
│
├── .env                            # Environment variables (gitignored)
├── config.py                       # Configuration loader
├── main.py                         # CLI entry point
├── requirements.txt                # Python dependencies
└── README.md
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

**GUI Mode (Recommended):**
```bash
python -m ui.app
```

**CLI Mode:**
```bash
python main.py
```

---

## GUI Overview

The modern GUI features:

| Component | Description |
|-----------|-------------|
| **Chat Area** | Messages displayed as chat bubbles with timestamps |
| **Input Bar** | Text input with send button and microphone button |
| **Waveform Visualizer** | Dual waveforms showing input (mic) and output (TTS) |
| **System Dashboard** | Live CPU, RAM, Disk charts with 60s history |
| **Quick Actions** | 10 tile buttons for common commands |

### Quick Action Buttons

| Button | Command |
|--------|---------|
| System | Check system status |
| Weather | Get current weather |
| Calendar | View upcoming events |
| Time | Get current time |
| VS Code | Launch VS Code |
| Browser | Open web browser |
| Add Event | Create calendar event |
| Find File | Search for files |
| Lock | Lock workstation |
| Music | Play music |

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
| "Add meeting Team standup tomorrow at 10am for 1 hour" | Add calendar event |
| "Schedule event Doctor appointment on Friday at 2pm" | Add calendar event |
| "Find resume" | Search for files |
| "System status" | Get CPU/RAM/Disk stats |

---

## Roadmap

- [x] Modern GUI with PySide6
- [x] Voice waveform visualization
- [x] Quick action tiles
- [x] System dashboard with charts
- [x] Chat bubble interface
- [x] Offline TTS fallback (pyttsx3)
- [x] Centralized logging system
- [x] Thread-safe conversation history
- [x] Optimized system monitoring (non-blocking CPU measurement)
- [x] Natural language calendar commands
- [x] File search with path validation and cancellation
- [ ] Email integration
- [ ] Smart notification system
- [ ] Advanced file manager with suggestions
- [ ] Auto-pilot mode with multi-step reasoning
- [ ] Emotional recognition and response adaptation

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

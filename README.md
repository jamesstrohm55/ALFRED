# A.L.F.R.E.D

> **All-Knowing Logical Facilitator for Reasoned Execution of Duties**

A.L.F.R.E.D is a modular, intelligent, and voice-enabled personal assistant inspired by J.A.R.V.I.S. It integrates multiple AI technologies, APIs, and system commands to create a cohesive and interactive digital assistant for personal and professional productivity.

---

## 🚀 Features

- 🎙️ **Voice Interaction**: Speech synthesis with ElevenLabs (text fallback if credits are exhausted)
- 🧠 **LLM-Powered Conversations**: Multi-layered LLM fallback (OpenAI, OpenRouter, Claude)
- 🗂️ **Memory System**: Store, recall, forget, and list facts about the user
- 💻 **System Monitoring**: Real-time CPU, RAM, Disk usage, uptime, and OS info
- 🌦️ **Weather Reports**: Get weather updates based on your current location
- 📅 **Calendar Management**: Integrate with Google Calendar to create and retrieve events
- 📁 **File Assistant**: Search, open, and delete files via voice/text commands
- 🖥️ **GUI Overlay**: Floating system monitor overlay
- 🔒 **System Automation**: Lock system, open apps, play music, shutdown
- 📝 **Command Logging**: Logs all commands to `command_log.txt`
- ⌨️ **Text Fallback Mode**: Automatically switches to text if microphone is not detected

---

## 📂 Project Structure
ALFRED/
│
├── core/ # Voice & brain logic
│ ├── __init__.py
│ ├── brain.py
│ ├── listener.py
│ ├── memory.py
│ ├── personality.py
│ └── voice.py
│
├── memory/ # Persistent memory system
│ └── memory_manager.py
│
├── service_commands/ # Modular command handlers
│ ├── calendar_commands.py
│ ├── file_assistant_commands.py
│ ├── memory_commands.py
│ ├── system_monitor_commands.py
│ ├── weather_commands.py
│
├── services/ # System & external services
│ ├── automation.py
│ ├── calendar_service.py
│ ├── file_assistant.py
│ ├── system_monitor.py
│ └── weather_service.py
│
├── ui/ # GUI components
│ ├── gui.py
│ └── system_overlay.py
│
├── utils/ # Utility functions
│ └── logger.py
│
├── command_log.txt # User command logs
├── config.py # API keys and configuration
├── main.py # Main application entry point
├── memory_store.json # Persistent memory storage
├── requirements.txt # Python dependencies
└── README.md # Project documentation


---

## ⚙️ Setup Instructions

### 1. Clone the Repository
    
    ```bash
    git clone https://github.com/jamesstrohm55/ALFRED.git
    cd ALFRED


### 2. Set Up Virtual Environment

    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate

### 3. Install Dependencies

    pip install -r requirements.txt

### 4. Configure API Keys

    OPENAI_KEY = "your_openai_api_key"
    OPENROUTER_API_KEY = "your_openrouter_api_key"
    ELEVENLABS_KEY = "your_elevenlabs_api_key"
    ALFRED_VOICE_ID = "your_elevenlabs_voice_id"
    WEATHER_API_KEY = "your_openweather_api_key"

### 5. Run Application

    python main.py

---


## 🛠 Usage Examples

"What is the weather today?"

"Remember that my favorite color is blue"

"What do you remember about my favorite color?"

"Forget my favorite color"

"Tell time"

"Find resume"

"What's on my calendar?"

"Create an event"

If no microphone is detected, the system prompts for text input.

---

## ✅ Roadmap

 Browser-based dashboard

 Email integration

 Smart notification system

 Advanced file manager with suggestions

 Auto-pilot mode with multi-step reasoning

 Emotional recognition and response adaptation

---

## 🤝 Contributing
We welcome contributions! To contribute:

Fork the repository

Create a feature branch: git checkout -b feature/feature-name

Commit your changes: git commit -m 'Add new feature'

Push to the branch: git push origin feature/feature-name

Open a Pull Request

---

## 📜 License
This project is licensed under the MIT License. See LICENSE for more information.

---

## 📣 Credits
Developed by James Strohm.

Inspired by the vision of AI assistants like J.A.R.V.I.S and powered by modern LLMs, APIs, and system tools.

“I am A.L.F.R.E.D, your logical facilitator. How may I assist you today?”
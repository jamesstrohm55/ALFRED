# A.L.F.R.E.D

> **All-Knowing Logical Facilitator for Reasoned Execution of Duties**

A modular AI assistant with a **FastAPI REST API**, **voice CLI**, and **PySide6 GUI** — all sharing one Supabase backend. Features a multi-provider LLM fallback chain, RAG pipeline with pgvector semantic memory, API key auth with per-user rate limiting, and per-user conversation sessions. Dockerized and deployed on Railway with GitHub Actions CI.

**[Live API Docs](https://alfred-production-5c1f.up.railway.app/docs)** · **[Live Demo](https://jamesstrohm.dev/projects/alfred-demo/)** · **[Portfolio](https://jamesstrohm.dev/projects/alfred.html)**

---

## Three Entry Points

| Mode | Command | Description |
|------|---------|-------------|
| **API** | `python -m api.run` | FastAPI REST + WebSocket server |
| **GUI** | `python -m ui.app` | PySide6 desktop application |
| **Voice CLI** | `python main.py` | Voice-activated command loop |
| **Docker** | `docker run -p 8000:8000 --env-file .env alfred` | Containerized API |

All three share the same Supabase backend for memory and conversation persistence.

---

## Features

### REST API
- **9 endpoints** + WebSocket with auto-generated OpenAPI docs
- **API key authentication** via `X-API-Key` header with SHA-256 hashed keys stored in Supabase
- **Per-user rate limiting** (configurable per key in the `api_users` table)
- **Per-user conversation sessions** — each API caller gets isolated conversation threads
- **User tracking** — conversations linked to `api_users` via foreign key

### AI & Memory
- **Multi-provider LLM fallback**: Nemotron 30B (free) → Claude 3.5 Sonnet → GPT-4o-mini
- **RAG pipeline**: Semantic search via pgvector + recent memories injected into every LLM query
- **Persistent memory**: Remember/recall/forget/search facts with auto-categorization and embeddings
- **Conversation persistence**: Chat history stored in Supabase, persists across sessions

### Voice & GUI
- **Voice interaction**: Google STT input + ElevenLabs/pyttsx3 TTS fallback chain
- **PySide6 GUI**: Chat bubbles, dual waveform visualizer, system dashboard, quick action tiles
- **Service integrations**: Google Calendar, OpenWeather, file manager, system monitoring

### Infrastructure
- **Docker**: Multi-stage build with `python:3.13-slim`, layer-cached dependencies
- **GitHub Actions CI**: Ruff lint + format check + pytest on every push/PR
- **70+ unit tests** with full mock coverage (no secrets needed in CI)
- **Pinned dependencies** with `pyproject.toml` packaging

---

## API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `POST` | `/chat` | Send a message, get AI response | Required |
| `GET` | `/chat/history` | Retrieve conversation history | Required |
| `POST` | `/memories` | Store a key-value memory | Required |
| `GET` | `/memories` | List all memories | Required |
| `GET` | `/memories/{key}` | Recall a specific memory | Required |
| `DELETE` | `/memories/{key}` | Forget a memory | Required |
| `POST` | `/memories/search` | Semantic vector search | Required |
| `GET` | `/system/health` | Health check + Supabase status | Public |
| `WS` | `/ws/chat` | Real-time WebSocket chat | Required |

### Example Usage

```bash
# Chat
curl -X POST https://alfred-production-5c1f.up.railway.app/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"message": "hello"}'

# Store a memory
curl -X POST https://alfred-production-5c1f.up.railway.app/memories \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"key": "favorite color", "value": "blue", "category": "personal"}'

# Health check (no auth needed)
curl https://alfred-production-5c1f.up.railway.app/system/health
```

---

## Project Structure

```
ALFRED/
├── api/                            # FastAPI REST API
│   ├── auth.py                     # API key auth + rate limiting
│   ├── models.py                   # Pydantic request/response schemas
│   ├── server.py                   # Endpoint handlers
│   └── run.py                      # Standalone entry point (uvicorn)
│
├── core/                           # Voice & brain logic
│   ├── brain.py                    # Command routing, LLM fallback, RAG
│   ├── listener.py                 # Speech recognition
│   ├── personality.py              # Persona configuration
│   └── voice.py                    # TTS (ElevenLabs + pyttsx3 fallback)
│
├── memory/                         # Persistent memory system
│   ├── database.py                 # Supabase client + embeddings
│   └── memory_manager.py           # Memory CRUD + semantic search
│
├── service_commands/               # Command handlers
│   ├── calendar_commands.py        # Natural language calendar parsing
│   ├── file_assistant_commands.py  # File operations
│   ├── memory_commands.py          # Remember/recall/forget/search
│   ├── system_monitor_commands.py  # System status queries
│   └── weather_commands.py         # Weather with IP geolocation
│
├── services/                       # External integrations
│   ├── automation.py               # OS commands (browser, VS Code, etc.)
│   ├── calendar_service.py         # Google Calendar API
│   ├── file_assistant.py           # File search/open/delete
│   ├── system_monitor.py           # CPU/RAM/Disk stats
│   └── weather_service.py          # OpenWeather + client IP geolocation
│
├── ui/                             # PySide6 GUI
│   ├── app.py                      # GUI entry point
│   ├── main_window.py              # Main window
│   ├── widgets/                    # Chat, waveform, dashboard, etc.
│   └── threads/                    # Background workers
│
├── tests/                          # Test suite (70+ tests)
│   ├── conftest.py                 # Shared fixtures & mocks
│   ├── test_api.py                 # API endpoints + auth + sessions
│   ├── test_brain.py               # Command routing & LLM tests
│   ├── test_database.py            # Supabase connectivity tests
│   ├── test_memory.py              # Memory CRUD & semantic search
│   └── test_services.py            # Service integration tests
│
├── .github/workflows/ci.yml        # GitHub Actions CI
├── Dockerfile                      # Production container
├── pyproject.toml                  # Packaging, ruff, mypy, pytest config
├── requirements.txt                # Pinned dependencies
├── config.py                       # Environment variable loader
├── main.py                         # Voice CLI entry point
└── LICENSE                         # MIT
```

---

## Setup

### 1. Clone & Install

```bash
git clone https://github.com/jamesstrohm55/ALFRED.git
cd ALFRED
python -m venv venv && source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file:

```env
OPENAI_KEY=your_openai_key
OPENROUTER_API_KEY=your_openrouter_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
XI_API_KEY=your_elevenlabs_key          # optional
XI_VOICE_ID=your_elevenlabs_voice_id    # optional
WEATHER_API_KEY=your_openweather_key    # optional
```

### 3. Supabase Schema

Create a project at [supabase.com](https://supabase.com), enable the `vector` extension, then run in the SQL Editor:

```sql
create extension if not exists vector;

create table memories (
  id bigint generated always as identity primary key,
  key text unique not null,
  value text not null,
  category text default 'general',
  tags text default '',
  embedding vector(1536),
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table conversations (
  id bigint generated always as identity primary key,
  session_id text not null,
  role text not null,
  content text not null,
  user_id uuid references api_users(id),
  timestamp timestamptz default now()
);

create table api_users (
  id uuid default gen_random_uuid() primary key,
  label text not null,
  api_key_hash text unique not null,
  rate_limit integer default 30,
  created_at timestamptz default now()
);

create table memory_metadata (
  key text primary key,
  value text not null
);

create index idx_memories_key on memories(key);
create index idx_conversations_session on conversations(session_id);
create index idx_conversations_user_id on conversations(user_id);
create index idx_api_users_key_hash on api_users(api_key_hash);

create or replace function match_memories(
  query_embedding vector(1536),
  match_threshold float default 0.5,
  match_count int default 5
)
returns table (id bigint, key text, value text, category text, similarity float)
language sql stable
as $$
  select memories.id, memories.key, memories.value, memories.category,
    1 - (memories.embedding <=> query_embedding) as similarity
  from memories
  where 1 - (memories.embedding <=> query_embedding) > match_threshold
  order by memories.embedding <=> query_embedding
  limit match_count;
$$;
```

### 4. Register an API Key

```sql
insert into api_users (label, api_key_hash, rate_limit) values (
  'my-key',
  encode(sha256(convert_to('your-chosen-key-string', 'UTF8')), 'hex'),
  30
);
```

### 5. Run

```bash
# API server
python -m api.run

# GUI
python -m ui.app

# Voice CLI
python main.py

# Docker
docker build -t alfred . && docker run -p 8000:8000 --env-file .env alfred
```

---

## Testing

```bash
pytest tests/ -v
```

70+ tests covering API endpoints, auth, sessions, brain routing, memory CRUD, semantic search, and service integrations. All external dependencies mocked — no API keys needed.

---

## License

MIT — see [LICENSE](LICENSE).

---

Developed by **James Strohm** · [jamesstrohm.dev](https://jamesstrohm.dev)

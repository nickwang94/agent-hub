# Agent Hub

A multi-agent collaboration system based on LangChain and LangGraph, with a modern ChatGPT-like web interface.

![Agent Hub UI](docs/screenshot.png)

## Features

- **Conversation Agent**: General conversational interaction
- **Researcher Agent**: Knowledge base Q&A with RAG
- **Session Management**: Multi-session support and history management
- **Multi-Agent Orchestration**: Intelligent routing using LangGraph
- **Knowledge Base**: Document loading and vector retrieval (ChromaDB)
- **Modern Web UI**: ChatGPT-like interface

## System Architecture

```
+------------------------------------------------------------------+
|                        Frontend (React)                           |
|                    http://localhost:5173                          |
|  +------------------------------------------------------------+  |
|  |  App.jsx / App.css                                          |  |
|  |  - Chat interface component                                  |  |
|  |  - Message history management                                |  |
|  |  - Session management                                        |  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+
                              |
                              | HTTP REST API
                              v
+------------------------------------------------------------------+
|                        Backend (Flask)                            |
|                    http://localhost:8080                          |
|  +------------------------------------------------------------+  |
|  |  api.py - REST API Entry Point                               |  |
|  |  - POST /chat           Chat endpoint                        |  |
|  |  - GET /sessions        Session list                         |  |
|  |  - DELETE /sessions/:id Delete session                       |  |
|  |  - POST /knowledge/add  Add knowledge                        |  |
|  |  - GET /knowledge/status Knowledge base status               |  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+
                              |
        +---------------------+---------------------+
        v                     v                     v
+----------------+  +----------------+  +----------------+
| orchestrator.py|  |session/manager |  |knowledge/store |
| LangGraph FSM  |  | Session Mgmt   |  | ChromaDB Vector|
| - Smart routing|  | - Create/Delete|  | - Doc storage  |
| - ChatAgent    |  | - History      |  | - Similarity   |
| - Researcher   |  | - Expiration   |  | - Metadata     |
+----------------+  +----------------+  +----------------+
        |
        v
+------------------------------------------------------------------+
|                    LLM Provider (DashScope)                       |
|              Alibaba Bailian - OpenAI Compatible                  |
|                    Models: qwen-plus / qwen-max                   |
+------------------------------------------------------------------+
```

### Core Modules

| Module | File | Description |
|--------|------|-------------|
| **Config** | `src/core/config.py` | Environment variables, API Key, model config |
| **LLM Client** | `src/core/llm.py` | LangChain LLM wrapper |
| **Chat Agent** | `src/agents/chat.py` | General conversation |
| **Researcher Agent** | `src/agents/researcher.py` | Knowledge base RAG Q&A |
| **Orchestrator** | `src/orchestrator.py` | LangGraph state machine, agent routing |
| **Knowledge Store** | `src/knowledge/store.py` | ChromaDB vector storage |
| **Document Loader** | `src/knowledge/loader.py` | Text/document parsing |
| **Session Manager** | `src/session/manager.py` | Session lifecycle management |

## Quick Start

### Requirements

- Python 3.10+
- Node.js 18+
- Alibaba Bailian API Key (get from https://bailian.console.aliyun.com/)

### 1. Install Backend Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

Or use the script:
```bash
./backend/bin/install.sh
```

### 2. Configure API Key

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your API Key:
```bash
# Alibaba Bailian API Key
DASHSCOPE_API_KEY=sk-your-api-key-here

# Model Configuration
LLM_MODEL=qwen-plus

# API Base URL
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 3. Start Backend Server

```bash
./backend/bin/start.sh
```

Backend will run at `http://localhost:8080`

### 4. Start Frontend

```bash
./frontend/bin/start.sh
```

Frontend will run at `http://localhost:5173`

Open your browser and visit http://localhost:5173 to start using!

## Project Structure

```
agent-hub/
├── backend/                  # Backend services
│   ├── bin/                  # Startup scripts
│   │   ├── install.sh        # Install dependencies
│   │   └── start.sh          # Start server
│   ├── data/                 # Data directory
│   │   └── chroma_db/        # ChromaDB vector database
│   ├── src/                  # Backend source code
│   │   ├── core/             # Core modules (config, LLM)
│   │   ├── agents/           # Agent definitions (Chat, Researcher)
│   │   ├── knowledge/        # Knowledge base (Store, Loader)
│   │   ├── session/          # Session management
│   │   └── orchestrator.py   # Multi-agent orchestration
│   ├── api.py                # Flask API entry point
│   ├── pyproject.toml        # Python dependencies
│   ├── venv/                 # Python virtual environment
│   └── .env                  # Environment configuration
├── frontend/                 # Frontend React application
│   ├── bin/                  # Startup scripts
│   │   ├── install.sh        # Install dependencies
│   │   └── start.sh          # Start server
│   ├── package.json          # Node.js dependencies
│   └── src/
│       ├── App.jsx           # Main application component
│       ├── App.css           # Styles
│       └── main.jsx          # Entry file
├── .env                      # Environment configuration (root)
├── .gitignore                # Git ignore file
└── README.md                 # Project documentation
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DASHSCOPE_API_KEY` | Alibaba Bailian API Key | Required |
| `LLM_MODEL` | Model name | `qwen-plus` |
| `LLM_BASE_URL` | API Base URL | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `CHROMA_PERSIST_DIR` | Knowledge base storage path | `./data/chroma_db` |

### Model Selection

| Model | Description | Use Case |
|-------|-------------|----------|
| `qwen-plus` | Balanced performance | General conversation, simple tasks |
| `qwen-max` | Best performance | Complex reasoning, code generation |
| `qwen-turbo` | Fast response | Real-time interaction, high concurrency |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Send chat message |
| `/sessions` | GET | Get session list |
| `/sessions/:id` | DELETE | Delete session |
| `/knowledge/add` | POST | Add knowledge to knowledge base |
| `/knowledge/status` | GET | Get knowledge base status |
| `/health` | GET | Health check |

### API Examples

```bash
# Send chat message
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Add knowledge
curl -X POST http://localhost:8080/knowledge/add \
  -H "Content-Type: application/json" \
  -d '{"text": "Python is a programming language"}'

# Get knowledge base status
curl http://localhost:8080/knowledge/status

# Get session list
curl http://localhost:8080/sessions

# Delete session
curl -X DELETE http://localhost:8080/sessions/<session_id>
```

## Common Commands

```bash
# Install backend dependencies
./backend/bin/install.sh

# Install frontend dependencies
./frontend/bin/install.sh

# Start backend server
./backend/bin/start.sh

# Start frontend server
./frontend/bin/start.sh

# Push to GitHub
git add . && git commit -m "message" && git push
```

## Development Guide

### Adding a New Agent

1. Create a new Agent class in `backend/src/agents/`
2. Extend `BaseAgent` and implement the `invoke` method
3. Add routing logic in `orchestrator.py`

```python
# src/agents/my_agent.py
from .base import BaseAgent

class MyAgent(BaseAgent):
    def invoke(self, state: dict) -> dict:
        # Implement your logic
        return state
```

### Modifying Frontend Styles

Edit `frontend/src/App.css` to customize the interface.

### Changing API Address

If the backend is not on the default port, edit `frontend/src/App.jsx`:

```javascript
const API_BASE_URL = 'http://localhost:8080'  // Change to your port
```

## Learning Resources

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Alibaba Bailian Documentation](https://help.aliyun.com/zh/dashscope/)

## License

MIT

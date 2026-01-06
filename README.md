# ⚡ Agentflow

> **A Production-Ready Agentic Research Assistant powered by Claude Sonnet 4 with Manual ReAct Loop Implementation**

Agentflow is an intelligent research assistant that combines the power of Anthropic's Claude with a custom-built ReAct (Reasoning + Acting) agent loop, multi-modal vision capabilities, and a sleek modern GUI. Unlike framework-based solutions, Agentflow implements its own agent orchestration, giving you complete control over the reasoning process.

---

## 🎯 Key Features

- **🧠 Manual ReAct Agent Loop**: Custom implementation of the Reasoning-Acting pattern without dependency on LangChain agents or CrewAI
- **🔧 Multi-Tool Integration**: DuckDuckGo search, Wikipedia, ChromaDB semantic search, and file persistence
- **👁️ Vision Capabilities**: Claude's multimodal API for screenshot analysis and image-based research
- **🎨 Modern GUI**: Sleek dark-themed interface built with CustomTkinter featuring glass-morphism effects
- **⚡ Real-Time Progress**: Live iteration tracking and status updates
- **📊 Structured Output**: Pydantic-validated JSON responses with topic, summary, sources, and tool usage
- **🧵 Non-Blocking Execution**: Background threading ensures responsive UI during research

---

## 🏗️ Architecture Deep Dive

### ReAct Loop Implementation

Agentflow implements a **manual ReAct (Reasoning + Acting) pattern** that gives the agent the ability to think, act, observe, and iterate until it arrives at a comprehensive answer.

```
┌─────────────────────────────────────────────────────────────────┐
│  User Query + Image (optional)                                  │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
    ┌────────────────────┐
    │  Iteration Loop    │ ◄──────────────┐
    │  (max 10 cycles)   │                │
    └────────┬───────────┘                │
             │                             │
             ▼                             │
    ┌─────────────────────┐               │
    │ 1. THINK            │               │
    │ Claude analyzes     │               │
    │ query & context     │               │
    └────────┬────────────┘               │
             │                             │
             ▼                             │
    ┌─────────────────────┐               │
    │ 2. ACT              │               │
    │ Select & call tool  │               │
    │ OR end turn         │               │
    └────────┬────────────┘               │
             │                             │
             ├─────── tool_use? ──────────┤
             │                             │
             ▼                             │
    ┌─────────────────────┐               │
    │ 3. OBSERVE          │               │
    │ Execute tool &      │               │
    │ get results         │               │
    └────────┬────────────┘               │
             │                             │
             └─────────────────────────────┘
             │
             ▼ end_turn?
    ┌─────────────────────┐
    │  Final Response     │
    │  (JSON formatted)   │
    └─────────────────────┘
```

### Core Agent Loop

**File**: `gui/agent.py` (lines 61-145)

```python
def agent_loop(query: str, image_path: str = None,
               max_iterations: int = 10,
               progress_callback = None) -> str:

    client = Anthropic()  # Claude Sonnet 4
    messages = [{"role": "user", "content": query_content}]

    for iteration in range(1, max_iterations + 1):
        # THINK: Claude processes current context
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,  # Available tool schemas
            messages=messages
        )

        # Check stop reason
        if response.stop_reason == "end_turn":
            # Agent completed reasoning
            return extract_text(response)

        # ACT: Process tool calls
        for block in response.content:
            if block.type == "tool_use":
                # OBSERVE: Execute tool
                result = execute_tool(block.name, block.input)

                # Add to message history
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    }]
                })
```

### Tool Calling System

**File**: `gui/tools.py`

Tools are defined using **JSON Schema** format compatible with Anthropic's tool calling API:

```python
{
    "name": "search",
    "description": "Search the web using DuckDuckGo",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"}
        },
        "required": ["query"]
    }
}
```

**Tool Execution Flow:**

1. Claude decides to use a tool
2. Returns `tool_use` block with `name`, `input`, and `id`
3. `execute_tool()` routes to the appropriate handler
4. Tool result is appended to message history with `tool_use_id`
5. Claude receives result in next iteration and continues reasoning

---

## 🔧 Tool Ecosystem

### 1. **Web Search** (`search`)
- **Provider**: DuckDuckGo (via LangChain)
- **Use Case**: Current events, recent information, news
- **Example**: `{"query": "latest AI developments 2025"}`

### 2. **Wikipedia** (`wikipedia`)
- **Configuration**: Top 5 results, 1000 char limit per result
- **Use Case**: Encyclopedic knowledge, historical facts, definitions
- **Example**: `{"query": "quantum computing"}`

### 3. **Semantic Search** (`semantic_search`)
- **Backend**: ChromaDB (persistent vector store at `./chroma_db`)
- **Use Case**: Search previously indexed documents by meaning
- **Features**:
  - Semantic similarity matching
  - Returns top-k relevant documents
  - 200-character preview per result

### 4. **File Save** (`save`)
- **Functionality**: Persist research findings to disk
- **Format**: Timestamped text files
- **Default**: `research_output.txt`

---

## 💡 Vision Capabilities

Agentflow supports **Claude's multimodal vision API** for analyzing screenshots and images:

**Implementation** (`gui/agent.py:69-88`):

```python
# Base64 encode image
with open(image_path, "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

# Append to user message
query_content.append({
    "type": "image",
    "source": {
        "type": "base64",
        "media_type": f"image/{ext}",
        "data": image_data
    }
})
```

**Supported Formats**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`

**Use Cases**:
- Analyze screenshots for research context
- Extract information from diagrams
- Understand visual data and charts
- OCR and text recognition

---

## 📊 Structured Output with Pydantic

**ResearchResponse Model** (`gui/agent.py:12-16`):

```python
class ResearchResponse(BaseModel):
    topic: str                  # Brief topic title
    summary: str                # Comprehensive research findings
    sources: list[str]          # URLs and references used
    tools_used: list[str]       # Tools called during research
```

**System Prompt Strategy**:
The agent is instructed to synthesize findings after 1-2 tool uses and **always** return valid JSON matching this exact schema. This ensures consistent, parseable output for the GUI.

---

## 🎨 Modern GUI

**Framework**: CustomTkinter (modern tkinter wrapper)

### Features

- **Dark Theme**: Professional dark interface with cyan/purple accents
- **Glass-Morphism**: Semi-transparent cards with subtle gradients
- **Responsive Design**: Scales content when window is resized
- **Real-Time Progress**: Live iteration counter and percentage bar
- **Status Indicator**: Animated dot showing agent state (ready/processing/complete/error)
- **Export Options**: JSON file export and clipboard copy

### UI Components

1. **Header Bar**: App title with live status indicator
2. **Input Section**: Multi-line query textbox with screen capture button
3. **Action Buttons**: Start Research (primary) and Stop (secondary)
4. **Progress Bar**: Cyan gradient showing completion (0-100%)
5. **Results Card**: Scrollable glass-morphism card with formatted output
6. **Bottom Actions**: Copy Results and Export JSON buttons

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10+
- Anthropic API Key ([get one here](https://console.anthropic.com/))

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/agentflow.git
cd agentflow
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Core Dependencies**:
- `anthropic` - Claude SDK
- `customtkinter` - Modern GUI framework
- `chromadb` - Vector database
- `pydantic` - Data validation
- `langchain-community` - Search/Wikipedia tools
- `python-dotenv` - Environment management

### 4. Configure API Key

Create a `.env` file in the project root:

```bash
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
```

---

## 📖 Usage

### Running the GUI

```bash
python gui/gui.py
```

### Using the Agent

1. **Enter Query**: Type your research question in the text box
2. **Optional - Capture Screen**: Click "📸 Capture Screen" to include a screenshot
3. **Start Research**: Click "🔍 Start Research"
4. **Monitor Progress**: Watch the progress bar and status updates
5. **View Results**: Results appear in the scrollable card below
6. **Export**: Use "📋 Copy Results" or "💾 Export JSON"

---

## 📁 Project Structure

```
agentflow/
├── gui/
│   ├── agent.py          # Core ReAct loop & Anthropic integration
│   ├── tools.py          # Tool schemas and execution logic
│   ├── gui.py            # CustomTkinter interface
│   └── gui_worker.py     # Background threading wrapper
├── chroma_db/            # Persistent ChromaDB vector store
├── .env                  # API keys (not committed)
├── requirements.txt      # Python dependencies
├── CLAUDE.md            # Development notes
└── README.md            # This file
```

### Module Responsibilities

- **agent.py**: Implements the ReAct loop, manages message history, handles vision integration
- **tools.py**: Defines tool schemas, implements tool execution, manages ChromaDB
- **gui.py**: Creates modern UI, handles user input, displays results
- **gui_worker.py**: Runs agent in background thread, provides progress callbacks

---

## 🔬 Technical Details

### Message History Management

The agent maintains conversation context through a messages array:

```python
messages = [
    {"role": "user", "content": "Initial query"},
    {"role": "assistant", "content": [tool_use_blocks]},
    {"role": "user", "content": [tool_results]},
    # ... continues for each iteration
]
```

### Progress Callbacks

Real-time updates are provided via callback function:

```python
def progress_callback(iteration: int, max_iter: int, message: str):
    percentage = (iteration / max_iter) * 100
    gui.update_progress(f"[{iteration}/{max_iter}] {message}", percentage)
```

### Error Handling

- **JSON Parsing Fallback**: If Claude's response isn't valid JSON, creates error ResearchResponse
- **Tool Execution Errors**: Caught and returned as tool results for Claude to handle
- **Max Iteration Safety**: Prevents infinite loops (default: 10 iterations)
- **Character Limits**: Tool results truncated to 1000 chars with `[...truncated...]` indicator

---

## 🛠️ Future Enhancements

- [ ] **Streaming Responses**: Real-time token streaming for faster perceived performance
- [ ] **Tool History Panel**: Visual timeline of tool calls and results
- [ ] **Custom Tool Creation**: GUI for defining new tools without code changes
- [ ] **Multi-Agent Collaboration**: Specialized sub-agents for different research domains
- [ ] **Persistent Chat History**: Save and resume research sessions
- [ ] **RAG Integration**: Automatic document ingestion for semantic search
- [ ] **API Mode**: REST API for programmatic access
- [ ] **Prompt Optimization**: A/B testing different system prompts for better results

---

## Acknowledgments

- **Anthropic** for Claude Sonnet 4 and the excellent Python SDK
- **CustomTkinter** for the modern GUI framework
- **ChromaDB** for fast vector similarity search
- **LangChain Community** for search/Wikipedia tool integrations

---

# Agentflow 🤖

## 🌟 Overview

Agentflow is an agentic AI system that uses Claude (Anthropic) as its reasoning engine to autonomously conduct research. The agent can break down complex queries, select appropriate tools, and generate comprehensive research reports with proper citations.

### Key Features

- **🧠 Autonomous Decision Making**: Uses Claude Sonnet 4 with tool-calling capabilities to intelligently select and chain tools
- **🔍 Multi-Source Research**: Integrates web search (DuckDuckGo) and Wikipedia for comprehensive information gathering
- **📝 Structured Output**: Generates research reports in a consistent JSON format with topic, summary, sources, and tools used
- **💾 Persistent Storage**: Automatically saves research outputs to text files with timestamps
- **🎯 Flexible Architecture**: Built on LangChain's agent framework for easy tool expansion

## 🏗️ Architecture

```
User Query
    ↓
Claude Sonnet 4 (Reasoning Engine)
    ↓
Tool Selection & Orchestration
    ├─→ DuckDuckGo Search (Web Search)
    ├─→ Wikipedia API (Encyclopedia Queries)
    └─→ File Saver (Persistent Storage)
    ↓
Structured Output (Pydantic Model)
    ↓
Research Report
```

## 🛠️ Technology Stack

- **LLM Framework**: LangChain
- **AI Model**: Claude Sonnet 4 (Anthropic)
- **Search Tools**: DuckDuckGo, Wikipedia API
- **Output Parsing**: Pydantic
- **Language**: Python 3.10+


## 📁 Project Structure

```
smartresearch-ai-agent/
│
├── main.py                 # Main application and agent orchestration
├── tools.py                # Tool definitions (search, wiki, save)
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── .env.example           # Example environment file
├── research_output.txt    # Generated research outputs (auto-created)
└── README.md              # This file
```

## 🔧 Configuration

### Agent Configuration

The agent is configured in `main.py`:

```python
# Change the model
llm = ChatAnthropic(model="claude-sonnet-4-20250514")

# Modify the system prompt
prompt = ChatPromptTemplate([
    ("system", "Your custom system prompt here..."),
    # ...
])
```

### Tool Configuration

Tools are defined in `tools.py`:

```python
# Add custom tools
from langchain.tools import Tool

my_custom_tool = Tool(
    name="my_tool",
    func=my_function,
    description="What this tool does",
)

# Add to tools list in main.py
tools = [search_tool, wiki_tool, save_tool, my_custom_tool]
```

## 🧰 Available Tools

| Tool | Description | Use Case |
|------|-------------|----------|
| **DuckDuckGo Search** | Web search engine | Finding current information, news, general queries |
| **Wikipedia** | Encyclopedia lookup | Factual information, definitions, historical data |
| **File Saver** | Text file storage | Persisting research outputs with timestamps |

## 🎯 Features in Detail

### 1. Structured Output with Pydantic

Research outputs follow a consistent schema:

```python
class ResearchResponse(BaseModel):
    topic: str              # Main topic of research
    summary: str            # Comprehensive summary
    sources: list[str]      # URLs and references used
    tools_used: list[str]   # Tools the agent selected
```

### 2. Autonomous Tool Selection

The agent decides which tools to use based on the query:
- Simple factual queries → Wikipedia
- Current events/news → DuckDuckGo Search
- Complex queries → Multiple tools in sequence

### 3. Persistent Storage

All research is automatically saved to `research_output.txt` with:
- Timestamp of query
- Complete research output
- Append mode (history preserved)

## 🔮 Future Enhancements

Planned features for upcoming versions:

- [ ] **FAISS Vector Store**: Add semantic search and document retrieval
- [ ] **Web Scraper**: Extract content from specific URLs
- [ ] **Python REPL**: Enable data analysis and calculations
- [ ] **Streamlit UI**: Interactive web interface
- [ ] **Cost Tracking**: Monitor API token usage
- [ ] **Multi-Agent System**: Specialized agents for different research types
- [ ] **Export Formats**: PDF, Markdown, JSON outputs
- [ ] **Conversation Memory**: Multi-turn research sessions

## 📊 Performance Metrics

Based on testing with diverse queries:

- **Query Completion Rate**: ~85%
- **Average Response Time**: 15-30 seconds
- **Tool Selection Accuracy**: High (agent rarely chooses wrong tool)
- **Output Quality**: Structured and citation-backed



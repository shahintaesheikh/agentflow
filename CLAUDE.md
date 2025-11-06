# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LangChain-based agentic AI research assistant that uses Claude (Anthropic) as the underlying LLM. The project creates a tool-calling agent that can help generate research papers with structured outputs.

## Architecture

**Core Components:**
- **LLM Integration**: Uses `langchain_anthropic.ChatAnthropic` with Claude Sonnet 4 (model: "claude-sonnet-4-20250514")
- **Agent Framework**: LangChain's `create_tool_calling_agent` and `AgentExecutor` for orchestration
- **Structured Output**: Uses Pydantic models with `PydanticOutputParser` to enforce response schema
- **Response Schema**: `ResearchResponse` model with fields: `topic`, `summary`, `sources`, `tools_used`

**Key Files:**
- `main.py`: Main agent implementation with prompt template, LLM configuration, and agent executor
- `tools.py`: Currently empty placeholder for future tool implementations
- `.env`: Contains `ANTHROPIC_API_KEY` for API authentication

## Development Commands

**Environment Setup:**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

**Running the Agent:**
```bash
python main.py
```

Note: The current implementation has a syntax error in the prompt template (line 32: missing comma after `("placeholder", "{chat_history}")`) and references undefined variable `query` (line 44). These need to be fixed before running.

## Known Issues

1. **Syntax Error**: `main.py:32` - Missing comma after `("placeholder", "{chat_history}")`
2. **Variable Reference**: `main.py:44` - `query` variable is not defined in scope
3. **Typo**: `main.py:33` - `agent_scratchapd` should likely be `agent_scratchpad`
4. **Empty Tools**: Agent is currently configured with empty tools list, limiting functionality

## Extension Points

To add new research capabilities:
1. Define custom tools in `tools.py` (e.g., Wikipedia search, web scraping, document retrieval)
2. Add tool instances to the `tools` parameter in both `create_tool_calling_agent()` and `AgentExecutor()`
3. Update the system prompt if needed to guide tool usage
4. Modify `ResearchResponse` model if additional output fields are required

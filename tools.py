from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import tool, ToolRuntime
from datetime import datetime

def save_to_txt(data: str, filename: str = "research_output.txt"):
    timestamp = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    formatted_text = f"-- Research Output -- \nTimestamp: {timestamp}\n\n{data}\n\n"

    with open(filename, "a", encoding = "utf-8") as f:
        f.write(formatted_text)
    
    return f"Data succesfully saved to {filename}"



search_tool = DuckDuckGoSearchRun(
    description="Tool for searching the web",
    verbose=True
)


api_wrapper = WikipediaAPIWrapper(
    top_k_results=5,
    doc_content_chars_max=1000,
)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)


def get_tool_schemas() -> list[dict]:
    """Return tool definitions in Claude Agent SDK format (JSON Schema)"""
    return [
        {
            "name": "search",
            "description": "Search the web for information using DuckDuckGo. Use this to find current information, news, and general web content.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find information about"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "wikipedia",
            "description": "Search Wikipedia for comprehensive information about topics. Use this for detailed reference material.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The topic to search for on Wikipedia"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "save",
            "description": "Save research findings to a text file for later reference.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "The research data/summary to save"
                    },
                    "filename": {
                        "type": "string",
                        "description": "The filename to save to (default: research_output.txt)"
                    }
                },
                "required": ["data"]
            }
        }
    ]


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool by name and return the result as a string"""
    try:
        if tool_name == "search":
            query = tool_input.get("query", "")
            if not query:
                return "Error: search query is required"
            result = search_tool.run(query)
        elif tool_name == "wikipedia":
            query = tool_input.get("query", "")
            if not query:
                return "Error: wikipedia query is required"
            result = wiki_tool.run(query)
        elif tool_name == "save":
            data = tool_input.get("data", "")
            filename = tool_input.get("filename", "research_output.txt")
            result = save_to_txt(data, filename)
        else:
            return f"Error: Tool '{tool_name}' not found. Available tools: search, wikipedia, save"

        # Convert result to string if needed
        result_str = str(result)

        # Summarize if too long (>1000 chars) to conserve tokens
        if len(result_str) > 1000:
            result_str = result_str[:800] + "\n[...truncated...]"

        return result_str
    except Exception as e:
        return f"Error executing tool '{tool_name}': {str(e)}"
from dotenv import load_dotenv
from pydantic import BaseModel
from anthropic import Anthropic
from tools import get_tool_schemas, execute_tool
import json
import os

load_dotenv()

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

SYSTEM_PROMPT = """You are a research assistant that helps generate research papers and synthesize information.

You have access to three tools:
1. search - Search the web using DuckDuckGo for current information
2. wikipedia - Search Wikipedia for detailed reference material
3. save - Save your research findings to a file

When answering queries:
- Use the search tool to find current information and news
- Use the wikipedia tool to get comprehensive background information
- Synthesize the information you find
- When you have gathered sufficient information, provide your final response as valid JSON

Your final response MUST be valid JSON with exactly these fields:
{
  "topic": "The main topic being researched",
  "summary": "A comprehensive summary of your findings",
  "sources": ["url1", "url2", ...],
  "tools_used": ["search", "wikipedia", ...]
}

Important: Return ONLY the JSON, no other text."""

def initialize_agent():
    client = Anthropic()
    tools = get_tool_schemas()
    return client, tools

def agent_loop(query: str, max_iterations: int = 10) -> str:
    """Run the agent loop for a research query"""
    client, tools = initialize_agent()

    messages = [{"role": "user", "content": query}]
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )

        #add response to message history
        messages.append({
            "role": "assistant",
            "content": response.content
        })

        # Check if we're done (stop_reason == "end_turn")
        if response.stop_reason == "end_turn":
            #extract the final text response
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""

        #execute any tools necessary
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input

                #execute the tool
                result = execute_tool(tool_name, tool_input)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        #Add tool to messages if any were executed
        if tool_results:
            messages.append({
                "role": "user",
                "content": tool_results
            })

    return "Max iterations reached without completion"


def run_research_query(query: str) -> ResearchResponse:
    """Output structured response"""
    response_text = agent_loop(query)

    #extract JSON from response
    try:
        #try to parse the entire response as JSON first
        result_dict = json.loads(response_text)
    except json.JSONDecodeError:
        #if that fails, try to find JSON in the response
        try:
            #look for JSON block in the response
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                result_dict = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: Could not parse response as JSON: {e}")
            print(f"Raw response: {response_text}")
            #Return a default response with the raw text
            result_dict = {
                "topic": "Unknown",
                "summary": response_text,
                "sources": [],
                "tools_used": []
            }

    #Convert to ResearchResponse
    try:
        result = ResearchResponse(**result_dict)
    except Exception as e:
        print(f"Warning: Could not convert response to ResearchResponse: {e}")
        #Return with raw data
        result = ResearchResponse(
            topic=result_dict.get("topic", "Unknown"),
            summary=result_dict.get("summary", ""),
            sources=result_dict.get("sources", []),
            tools_used=result_dict.get("tools_used", [])
        )

    return result

if __name__ == "__main__":
    #Get user input
    query = input("What can I help you research?\n")

    #Optional screenshot functionality (for future implementation)
    ss_want = input("Would you like to submit a screenshot? (y/n): ").lower().strip()
    if ss_want in ["y", "yes"]:
        ss_path = input("Enter the file path to the screenshot: ")
        if os.path.exists(ss_path):
            query = f"Please analyze this screenshot and research related topics: {query}\n[Screenshot will be added in Phase 1b]"
        else:
            print(f"Screenshot file not found: {ss_path}")

    print(f"Running query: {query}\n")
    response = run_research_query(query)

    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Topic: {response.topic}")
    print(f"\nSummary:\n{response.summary}")
    print(f"\nSources: {', '.join(response.sources) if response.sources else 'None'}")
    print(f"\nTools Used: {', '.join(response.tools_used) if response.tools_used else 'None'}")

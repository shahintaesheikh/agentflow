from dotenv import load_dotenv
from pydantic import BaseModel
from anthropic import Anthropic
from tools import get_tool_schemas, execute_tool
import json
import os
import base64
from pathlib import Path

load_dotenv()

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

SYSTEM_PROMPT = """You are a research assistant. Use tools to find information, then respond with ONLY valid JSON.

Tools available: search (web), wikipedia, save (file).

ALWAYS respond in this JSON format and ONLY JSON:
{
  "topic": "Brief topic title",
  "summary": "Comprehensive summary of findings",
  "sources": ["url1", "url2"],
  "tools_used": ["search", "wikipedia", "save"]
}

After 1-2 tool uses, synthesize findings into the JSON response immediately."""

def initialize_agent():
    client = Anthropic()
    tools = get_tool_schemas()
    return client, tools

def load_image_as_base64(image_path: str) -> str:
    """Load an image file and encode it as base64"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.standard_b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Could not load image: {e}")

def get_image_media_type(image_path: str) -> str:
    """Determine the media type based on file extension"""
    extension = Path(image_path).suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp"
    }
    return media_types.get(extension, "image/jpeg")

def agent_loop(query: str, image_path: str = None, max_iterations: int = 10) -> str:
    """Run the agent loop for a research query, optionally with an image"""
    client, tools = initialize_agent()

    # Build the initial message with optional image
    user_content = []

    #Image analysis 
    if image_path and os.path.exists(image_path):
        try:
            image_data = load_image_as_base64(image_path)
            media_type = get_image_media_type(image_path)
            user_content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": image_data
                }
            })
        except Exception as e:
            print(f"Warning: Could not load image: {e}")

    # Add text query
    user_content.append({
        "type": "text",
        "text": query
    })

    messages = [{"role": "user", "content": user_content}]
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


def run_research_query(query: str, image_path: str = None) -> ResearchResponse:
    """Output structured response, optionally with image analysis"""
    response_text = agent_loop(query, image_path=image_path)

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

    # Optional screenshot functionality
    image_path = None
    ss_want = input("Would you like to submit a screenshot? (y/n): ").lower().strip()
    if ss_want in ["y", "yes"]:
        ss_path = input("Enter the file path to the screenshot: ").strip()
        if ss_path and os.path.exists(ss_path):
            image_path = ss_path
            query = f"Please analyze this screenshot and answer the following question: {query}"
            print(f"Screenshot loaded: {ss_path}")
        else:
            print(f"Screenshot file not found: {ss_path}")

    print(f"\nRunning query: {query}\n")
    response = run_research_query(query, image_path=image_path)

    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Topic: {response.topic}")
    print(f"\nSummary:\n{response.summary}")
    print(f"\nSources: {', '.join(response.sources) if response.sources else 'None'}")
    print(f"\nTools Used: {', '.join(response.tools_used) if response.tools_used else 'None'}")

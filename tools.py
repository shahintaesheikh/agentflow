from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import tool, ToolRuntime
from datetime import datetime
import numpy as np

def save_to_txt(data: str, filename: str = "research_output.txt"):
    timestamp = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    formatted_text = f"-- Research Output -- \nTimestamp: {timestamp}\n\n{data}\n\n"

    with open(filename, "a", encoding = "utf-8") as f:
        f.write(formatted_text)

    return f"Data succesfully saved to {filename}"

# Global FAISS variables - initialized when documents are indexed
embedding_model = None
faiss_index = None
documents = []

def semantic_search(query: str, top_k: int = 5) -> str:
    """Execute semantic search against indexed documents"""
    # Check if FAISS is initialized
    if faiss_index is None or embedding_model is None:
        return "Error: FAISS index not initialized. No documents have been indexed yet."

    if len(documents) == 0:
        return "Error: No documents in index."

    try:
        # Embed the query
        query_embedding = embedding_model.encode([query])[0]
        query_embedding = np.array([query_embedding], dtype=np.float32)

        # Search FAISS index
        distances, indices = faiss_index.search(query_embedding, min(top_k, len(documents)))

        # Retrieve and format results
        results = []
        for i, idx in enumerate(indices[0]):
            doc_preview = documents[idx][:200] if len(documents[idx]) > 200 else documents[idx]
            results.append(f"Match {i+1}: {doc_preview}...")

        return "\n".join(results) if results else "No matching documents found"
    except Exception as e:
        return f"Error in semantic search: {str(e)}"

def initialize_faiss_index(docs_list, embedding_model_name='all-MiniLM-L6-v2'):
    """Initialize FAISS index with documents"""
    global embedding_model, faiss_index, documents
    try:
        from sentence_transformers import SentenceTransformer
        from faiss import IndexFlatL2

        embedding_model = SentenceTransformer(embedding_model_name)
        documents = docs_list

        # Create embeddings
        embeddings = embedding_model.encode(docs_list)
        embeddings = np.array(embeddings, dtype=np.float32)

        # Create FAISS index
        faiss_index = IndexFlatL2(embeddings.shape[1])
        faiss_index.add(embeddings)

        return f"FAISS index initialized with {len(docs_list)} documents"
    except ImportError:
        return "Error: sentence-transformers or faiss not installed. Run: pip install sentence-transformers faiss-cpu"
    except Exception as e:
        return f"Error initializing FAISS: {str(e)}"


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
        },
        {
            "name": "semantic_search",
            "description": "Search through indexed documents using semantic similarity. Finds relevant documents based on meaning.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The semantic search query"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)"
                    }
                },
                "required": ["query"]
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
        elif tool_name == "semantic_search":
            query = tool_input.get("query", "")
            top_k = tool_input.get("top_k", 5)
            result = semantic_search(query, top_k)
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
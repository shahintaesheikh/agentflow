from dotenv import load_dotenv
from dataclasses import dataclass
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_agent
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import VectorStoreRetriever
from langgraph.checkpoint.memory import InMemorySaver
from tools import search_tool, wiki_tool

load_dotenv()

@dataclass
class Context:
    user_id: str

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

llm = ChatAnthropic(model = "claude-sonnet-4-20250514")

parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate(
    [
        (
            "system",
            """
            You are a research assistant that will help generate a research paper.
            Answer the user query and use necessary tools.
            Wrap the output in this format and provide no other text\n{format_instructions}
            """
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions = parser.get_format_instructions())

checkpointer = InMemorySaver()

tools = [search_tool, wiki_tool]

agent = create_agent(
    model = "claude-sonnet-4-20250514",
    tools = tools,
    system_prompt=prompt,
    response_format=ResearchResponse,
    checkpointer=InMemorySaver
)

#agent_executor = AgentExecutor(agent = agent, tools = tools, verbose=True)

def run_research_query(query: str) -> ResearchResponse:
    raw_response = agent.invoke({"input": query})

    #exctract text from agent response
    output = raw_response["output"]
    if isinstance(output, list) and len(output) > 0:
        output = output[0].get("text", "") if isinstance(output[0], dict) else str(output[0])

    result = parser.parse(output)
    return result

if __name__ == "__main__":
    #test queries
    query = input("What can I help you research?\n")
    ss_want = input("Would you like to submit a screenshot?\n")
    if ss_want:
        ss_query = input("Attach the file path here: ")

    print(f"Running query: {query}\n")
    response = run_research_query(query)

    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Topic: {response.topic}")
    print(f"\nSummary:\n{response.summary}")
    print(f"\nSources: {response.sources}")
    print(f"\nTools Used: {response.tools_used}")
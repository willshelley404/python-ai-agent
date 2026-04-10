# research_agent_modern.py

# --- Python 3.13 fix ---
import builtins
import uuid
builtins.uuid = uuid

from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq
from langchain.agents import create_agent

from tools import search_tool, financial_tool

# ----------------------------
# Load env
# ----------------------------
load_dotenv()

# ----------------------------
# Output schema
# ----------------------------
class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

parser = PydanticOutputParser(pydantic_object=ResearchResponse)

# ----------------------------
# LLM
# ----------------------------
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

# ----------------------------
# Agent
# ----------------------------
agent = create_agent(
    model=llm,
    tools=[search_tool, financial_tool]
)

# ----------------------------
# Prompt builder
# ----------------------------
FORMAT_INSTRUCTIONS = parser.get_format_instructions()

def build_query(user_query: str) -> str:
    return f"""
    You are a research assistant.

    TOOL RULES:
    - Use financial_tool ONLY for:
    stocks, tickers, WTI, CPI, GDP, unemployment
    - Use web_search for:
    general knowledge (people, history, facts)

    IMPORTANT:
    - Always call the correct tool
    - If a tool returns data, you MUST use it

    Return ONLY valid JSON:
    {FORMAT_INSTRUCTIONS}

    User query:
    {user_query}
    """

# ----------------------------
# CLI
# ----------------------------
if __name__ == "__main__":
    print("\n🔎 Research Agent Ready\n")

    while True:
        query = input("Enter query (or 'exit'):\n> ")
        if query.lower() == "exit":
            break

        try:
            raw_response = agent.invoke({
                "messages": [
                    {"role": "user", "content": build_query(query)}
                ]
            })

            output_text = raw_response["messages"][-1].content

            structured = parser.parse(output_text)

            print("\n=== STRUCTURED OUTPUT ===\n")
            print(structured)
            print("\nTopic:", structured.topic)
            print("Summary:", structured.summary)
            print("Sources:", structured.sources)
            print("Tools Used:", structured.tools_used)

        except Exception as e:
            print("\n❌ Error:", e)
            print("Raw response:", raw_response if "raw_response" in locals() else "None")
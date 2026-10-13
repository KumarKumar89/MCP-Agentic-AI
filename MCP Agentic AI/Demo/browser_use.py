"""
Basic usage example for mcp_use.

This example demonstrates how to use the mcp_use library with MCPClient
to connect any LLM to MCP tools through a unified interface.

Special thanks to https://github.com/microsoft/playwright-mcp for the server.
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from mcp_use import MCPAgent, MCPClient


def create_llm():
    """Use a free local LLM by default; Groq is only used when explicitly enabled."""
    load_dotenv()

    if os.getenv("USE_LOCAL_LLM", "true").lower() not in {"0", "false", "no"}:
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        model_name = os.getenv("FREE_LLM_MODEL", "llama3.2:3b")
        return ChatOpenAI(
            base_url=ollama_base_url,
            api_key="ollama",
            model=model_name,
            temperature=0,
        )

    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        from langchain_groq import ChatGroq

        return ChatGroq(api_key=groq_key, model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"))

    raise RuntimeError("No free local model or Groq key is configured.")


async def main():
    """Run the example using a configuration file."""
    # Create MCPClient from config file
    client = MCPClient.from_config_file(os.path.join(os.path.dirname(__file__), "browser_mcp.json"))

    llm = create_llm()

    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=30)

    # Run the query
    result = await agent.run(
        "Find the best restaurant in San Francisco BROWSER USING GOOGLE SEARCH",
        max_steps=30,
    )
    print(f"\nResult: {result}")


if __name__ == "__main__":
    # Run the appropriate example
    asyncio.run(main())

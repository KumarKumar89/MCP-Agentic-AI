"""
Example demonstrating how to use mcp_use with Airbnb.

This example shows how to connect an LLM to Airbnb through MCP tools
to perform tasks like searching for accommodations.

Special Thanks to https://github.com/openbnb-org/mcp-server-airbnb for the server.
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from mcp_use import MCPAgent, MCPClient


def create_llm():
    """Use the local Ollama model."""
    load_dotenv()

    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    model_name = os.getenv("FREE_LLM_MODEL", "llama3.2:3b")
    return ChatOpenAI(
        base_url=ollama_base_url,
        api_key="ollama",
        model=model_name,
        temperature=0,
    )


async def run_airbnb_example():
    """Run an example using Airbnb MCP server."""
    # Create MCPClient with Airbnb configuration
    client = MCPClient.from_config_file(os.path.join(os.path.dirname(__file__), "airbnb_mcp.json"))
    llm = create_llm()

    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=30)

    try:
        # Run a query to search for accommodations
        result = await agent.run(
             "Find me a place to stay in Barcelona for 2 adults "
            "for one week, starting November 1st, 2025. Show me the top 3 options.",
            max_steps=30,
        )
        print(f"\nResult: {result}")
    finally:
        # Ensure we clean up resources properly
        if client.sessions:
            await client.close_all_sessions()


if __name__ == "__main__":
    asyncio.run(run_airbnb_example())

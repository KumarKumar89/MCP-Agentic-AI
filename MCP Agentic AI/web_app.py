import os
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

app = FastAPI(title="MCP-Agentic-AI Web UI", version="1.0.0")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, "mcp_demo_interface.html")


def create_llm():
    """Prefer the free local Ollama model; fall back to valid Groq settings only if configured."""
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

    raise RuntimeError("No free local model or Groq API key is configured.")


async def run_agent(script_name: str, query: str) -> str:
    if script_name == "browser_use":
        config_file = os.path.join(BASE_DIR, "Demo", "browser_mcp.json")
        agent_kwargs = {"max_steps": 30}
    elif script_name == "airbnb_use":
        config_file = os.path.join(BASE_DIR, "Demo", "airbnb_mcp.json")
        agent_kwargs = {"max_steps": 30}
    elif script_name == "chat_example":
        config_file = os.path.join(BASE_DIR, "Demo", "browser_mcp.json")
        agent_kwargs = {"max_steps": 15, "memory_enabled": True}
    else:
        raise ValueError(f"Unsupported script: {script_name}")

    client = MCPClient.from_config_file(config_file)
    llm = create_llm()

    try:
        agent = MCPAgent(llm=llm, client=client, **agent_kwargs)
        result = await agent.run(query, max_steps=agent_kwargs.get("max_steps", 15))
        return str(result)
    finally:
        if getattr(client, "sessions", None):
            await client.close_all_sessions()


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(HTML_FILE)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/run")
async def api_run(request: Request) -> JSONResponse:
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({"output": "Invalid JSON body."}, status_code=400)

    script_name = str(payload.get("script", "browser_use"))
    user_query = str(payload.get("query", "")).strip()

    if not user_query:
        return JSONResponse({"output": "Please enter a prompt before running the agent."}, status_code=400)

    try:
        answer = await run_agent(script_name, user_query)
        return JSONResponse({"output": answer})
    except Exception as exc:  # pragma: no cover - runtime error surfaced to UI
        return JSONResponse({"output": f"Error: {exc}"}, status_code=500)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("web_app:app", host="0.0.0.0", port=8000, reload=False)

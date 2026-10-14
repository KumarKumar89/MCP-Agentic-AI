import asyncio
import json
import os
import time
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

app = FastAPI(title="MCP-Agentic-AI Web UI", version="1.1.0")
# Enable CORS so the frontend can be hosted on a different origin if needed.
# In production, restrict allow_origins to the specific frontend origin(s).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, "mcp_demo_interface.html")
APP_HOST = os.getenv("HOST", "0.0.0.0")
APP_PORT = int(os.getenv("PORT", "1455"))

# script_name -> (config file, agent kwargs, default query)
SCRIPTS: dict[str, tuple[str, dict[str, Any], str]] = {
    "browser_use": (
        "Demo/browser_mcp.json",
        {"max_steps": 30, "memory_enabled": False},
        "Find the best restaurant in San Francisco USING GOOGLE SEARCH",
    ),
    "airbnb_use": (
        "Demo/airbnb_mcp.json",
        {"max_steps": 30, "memory_enabled": False},
        "Find me a place to stay in Barcelona for 2 adults for one week, starting November 1st. Show me the top 3 options.",
    ),
    "chat_example": (
        "Demo/browser_mcp.json",
        {"max_steps": 15, "memory_enabled": True},
        "Search Google for the weather in Tokyo",
    ),
}


def create_llm():
    """Create the local Ollama chat model."""
    load_dotenv()
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    model_name = os.getenv("FREE_LLM_MODEL", "llama3.2:3b")
    return ChatOpenAI(
        base_url=ollama_base_url,
        api_key="ollama",
        model=model_name,
        temperature=0,
    )

def sse(event: str, data: Any) -> str:
    """Format one Server-Sent Event for the live output stream."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def flatten_content(content: Any) -> str:
    """Flatten LangChain message content (str or content blocks) into text."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(str(item.get("text", "")))
            else:
                parts.append(str(item))
        return "\n".join(p for p in parts if p)
    return str(content)


async def run_agent_stream(script_name: str, query: str):
    """Run the MCP agent and yield UI events (logs, tool steps, final answer) via SSE."""
    if script_name not in SCRIPTS:
        yield sse("error", {"message": f"Unsupported script: {script_name}"})
        return

    config_rel, agent_options, _default_query = SCRIPTS[script_name]
    config_file = os.path.join(BASE_DIR, config_rel)

    started = time.time()
    yield sse("log", {"text": f"Initializing MCP client…  [{config_rel}]"})

    try:
        client = MCPClient.from_config_file(config_file)
    except Exception as exc:
        yield sse("error", {"message": f"Could not load MCP config: {exc}"})
        return

    try:
        llm = create_llm()
    except Exception as exc:
        yield sse("error", {"message": f"LLM unavailable: {exc} Ensure Ollama is running."})
        return

    model_name = getattr(llm, "model_name", None) or getattr(llm, "model", "?")
    servers = ", ".join(client.get_servers()) if hasattr(client, "get_servers") else "?"
    yield sse("log", {"text": f"LLM ready: {model_name} · server(s): {servers}"})

    agent_kwargs = dict(agent_options)
    max_steps = int(agent_kwargs.pop("max_steps", 15))
    agent = MCPAgent(llm=llm, client=client, max_steps=max_steps, **agent_kwargs)

    try:
        yield sse("log", {"text": "Connecting to MCP server(s) and discovering tools…"})
        await agent.initialize()
        tool_names = [getattr(t, "name", "?") for t in getattr(agent, "_tools", [])]
        yield sse("connected", {"tools": tool_names, "count": len(tool_names)})

        step_no = 0
        answer: str | None = None
        async for item in agent.stream(query, max_steps=max_steps, manage_connector=False):
            if isinstance(item, tuple):  # (AgentAction, observation)
                step_no += 1
                action, observation = item
                tool = getattr(action, "tool", "?")
                args = getattr(action, "tool_input", {})
                thought = flatten_content(getattr(action, "log", ""))[:300]
                obs = flatten_content(observation)
                yield sse(
                    "tool",
                    {
                        "step": step_no,
                        "of": max_steps,
                        "tool": tool,
                        "args": args,
                        "thought": thought,
                        "result": obs[:700],
                    },
                )
            else:
                answer = flatten_content(item)

        if answer is None:
            answer = "Agent finished without a final answer."
        yield sse("done", {"text": answer, "steps": step_no, "elapsed": round(time.time() - started, 1)})
    except asyncio.CancelledError:
        raise
    except Exception as exc:  # surface real errors to the UI instead of hanging
        yield sse("error", {"message": f"{type(exc).__name__}: {exc}"})
    finally:
        try:
            await agent.close()
        except Exception:
            pass


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(HTML_FILE, headers={"Cache-Control": "no-store"})


@app.get("/api/config")
async def api_config() -> dict[str, Any]:
    """Expose per-script defaults so the UI always matches the backend."""
    load_dotenv()
    return {
        "scripts": {
            name: {"config": cfg, "agent": kwargs, "defaultQuery": dq}
            for name, (cfg, kwargs, dq) in SCRIPTS.items()
        }
    }


@app.get("/health")
async def health() -> dict[str, Any]:
    load_dotenv()
    return {
        "status": "ok",
        "scripts": sorted(SCRIPTS),
        "llm": "local-ollama",
    }


@app.post("/api/run")
async def api_run(request: Request):
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({"output": "Invalid JSON body."}, status_code=400)

    script_name = str(payload.get("script", "browser_use"))
    user_query = str(payload.get("query", "")).strip()

    if not user_query:
        return JSONResponse({"output": "Please enter a prompt before running the agent."}, status_code=400)
    if script_name not in SCRIPTS:
        return JSONResponse({"output": f"Unsupported script: {script_name}"}, status_code=400)

    return StreamingResponse(
        run_agent_stream(script_name, user_query),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("web_app:app", host=APP_HOST, port=APP_PORT, reload=False)

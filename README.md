MCP-USE Setup Guide
**\*\*\*\***\***\*\*\*\*** use python 3.11+ version **\*\*\*\***\*\***\*\*\*\*** This guide will help you set up and configure the mcp-use repository for use with Ollama and Cursor.

🔧 Setup Instructions

1. Clone the Repository
   Use the following command to clone the repo:
   git clone https://github.com/mcp-use/mcp-use.git

2. Create a Virtual Environment
   Set up a Python virtual environment in your project directory:
   python -m venv venv
   source venv/bin/activate # On Windows use: venv\Scripts\activate

3. Use the Local Ollama Model
   Demo scripts use Ollama locally by default. Set OLLAMA_BASE_URL and FREE_LLM_MODEL in .env to customize the model.

4. Locate the Example Config File
   Inside the Demo folder, you'll find various configuration files. Choose the appropriate one based on your use case.

5. Add Config to Cursor Settings
   Take the selected config (e.g., examples/browser_mcp.json) and paste its content into Cursor's MCP Settings.
   📌 Example configuration from examples/browser_mcp.json:
   {
   "mcpServers": {
   "playwright": {
   "command": "npx",
   "args": ["@playwright/mcp@latest"],
   "env": {
   "DISPLAY": ":1"
   }
   }
   }
   }

Paste this in Cursor settings under the MCP section:

Example:

OUTPUT :

# Output Explanation of This Repo (List-Wise)

This repo is a **demo/tutorial project** built on top of [mcp-use](https://github.com/mcp-use/mcp-use). It connects LLMs (local Ollama by default, plus provider-specific examples) to MCP servers (Playwright, Airbnb, Filesystem, Blender). Below is what each script **outputs** when you run it.

---

## 📁 `Demo/` folder

### 1. `browser_use.py` → Web Browsing Output

- **Input query:** _"Find the best restaurant in San Francisco BROWSER USING GOOGLE SEARCH"_
- **Server used:** Playwright MCP (`browser_mcp.json`)
- **Output:** Agent opens a browser via Playwright, performs a Google search, reads results, and prints a **final text answer** like:
  ```
  Result: The best restaurants in San Francisco are X, Y, Z ...
  ```
- Console also shows step-by-step tool calls (browser navigate, click, read page).

### 2. `chat_example.py` → Interactive Chat Output

- **Output is a live terminal chat loop:**

  ```
  Initializing chat...
  ===== Interactive MCP Chat =====
  Type 'exit' or 'quit' to end the conversation
  Type 'clear' to clear conversation history
  ==================================

  You: <your question>
  Assistant: <answer with memory of previous messages>
  ```

- Keeps **conversation history** (memory_enabled=True). `clear` resets it, `exit` quits.

### 3. `airbnb_use.py` → Airbnb Search Output

- **Input query:** _"Find me a place to stay in Barcelona for 2 adults for one week, starting November 1st, 2026. Show me the top 3 options."_
- **Server used:** `@openbnb/mcp-server-airbnb`
- **Output:** A printed **"Result:"** paragraph listing the **top 3 Airbnb listings** (name, price, rating, link).

### 4. `blender_use.py` → 3D Scene Creation Output

- **Input query:** _"Create an inflatable cube with soft material and a plane as ground."_
- **Server used:** `blender-mcp` (via `uvx`, needs Blender addon running)
- **Output:** Prints `Result: ...` confirming the cube + plane were created **inside the Blender app** (visual output appears in Blender's 3D viewport, not the terminal).
- ⚠️ Uses `ChatAnthropic` (needs Anthropic API key).

---

## 📁 `for_practice/` folder

### 5. `filesystem_use.py` → File Listing Output

- **Input query:** _"Hello can you give me a list of files and directories in the current directory"_
- **Server used:** `@modelcontextprotocol/server-filesystem`
- **Output:** `Result: ...` followed by a **list of files/folders** in the configured directory.
- ⚠️ Hardcoded path `/home/pietro/projects/mcp-use/` — change it to your own path.

### 6. `multi_server_example.py` → Combined Multi-Server Output

- **Input query:** _"Search for a nice place to stay in Barcelona on Airbnb, then use Google to find nearby restaurants and attractions. Write the result in the current directory in restarant.txt"_
- **Servers used:** Airbnb + Playwright + Filesystem (**3 servers at once**)
- **Output:**
  1. Airbnb search results
  2. Google search results for restaurants/attractions
  3. A new file **`restarant.txt`** created on disk containing the combined results
  4. Final summary printed to terminal.

### 7. `http_example.py` → Remote (HTTP/SSE) Server Output

- Connects to a Playwright MCP server already running on `http://localhost:8931/sse`
- **Input query:** _"Find the best restaurant in San Francisco USING GOOGLE SEARCH"_
- **Output:** Same as browser_use.py — Google search results summarized as text.
- ⚠️ Uses `ChatOpenAI(model="gpt-4o")` — needs OpenAI key. You must first run `npx @playwright/mcp@latest --port 8931` in another terminal.

---

## 🔑 Common Output Pattern (All Scripts)

Every script follows the same console output flow:

1. **Initialization** – connects to MCP server, discovers available tools
2. **Agent steps** – LLM decides which MCP tool to call (browser, search, file ops…)
3. **`Result: <final natural-language answer>`** – printed at the end

## ⚠️ Key Notes

- **Default LLM is free local Ollama** (`llama3.2:3b`) in Demo scripts — set `OLLAMA_BASE_URL` and `FREE_LLM_MODEL` in `.env` to customize it.
- `blender_use.py`, `multi_server_example.py`, and `http_example.py` still use **Anthropic/OpenAI** directly — they will fail without those API keys.
- You need **Node.js (npx)** installed for the MCP servers to launch.

# 🧠 MCP (Model Context Protocol) — Complete Beginner's Guide

---

## 📌 1. WHAT is MCP?

MCP is an **open protocol** (like USB for AI apps) that standardizes how **AI models** connect to **external data sources, tools, and services**.

```
┌─────────────────────────────────────────────────────────┐
│                    MCP AT A GLANCE                       │
│                                                          │
│   AI Model ◄──── MCP Protocol ────► External World       │
│  (Claude,          (JSON-RPC         (Files, DBs, APIs,  │
│   GPT, etc.)        over stdio/HTTP)  HTML, Tools...)    │
│                                                          │
│   Before MCP:  Every AI app = custom glue code 😫        │
│   After MCP:   One standard protocol = plug & play 🎉    │
└─────────────────────────────────────────────────────────┘
```

---

## 📌 2. WHY MCP? (The Problem It Solves)

```
❌ BEFORE MCP:
   ┌──────────┐    custom code    ┌──────────┐
   │ AI Model │ ◄──────────────►  │ Database │
   └──────────┘    custom code    └──────────┘
   ┌──────────┐    custom code    ┌──────────┐
   │ AI Model │ ◄──────────────►  │ File Sys │
   └──────────┘    custom code    └──────────┘
   ┌──────────┐    custom code    ┌──────────┐
   │ AI Model │ ◄──────────────►  │ API      │
   └──────────┘    custom code    └──────────┘
   = M × N integrations 😵

✅ AFTER MCP:
   ┌──────────┐                    ┌──────────┐
   │ AI Model │ ◄── MCP ────────►  │ MCP Server│ (Database)
   └──────────┘                    └──────────┘
   ┌──────────┐                    ┌──────────┐
   │ AI Model │ ◄── MCP ────────►  │ MCP Server│ (Files)
   └──────────┘                    └──────────┘
   ┌──────────┐                    ┌──────────┐
   │ AI Model │ ◄── MCP ────────►  │ MCP Server│ (API)
   └──────────┘                    └──────────┘
   = M + N integrations 😊
```

---

## 📌 3. IPO MODEL (Input → Process → Output)

```
┌─────────────────────────────────────────────────────┐
│                 MCP IPO FLOW                        │
│                                                      │
│  INPUT:  User asks AI → "Read file X"                │
│          │                                           │
│          ▼                                           │
│  PROCESS:                                            │
│    ┌─────────────┐    JSON-RPC     ┌──────────────┐ │
│    │  AI (Client)│ ──────────────► │  MCP Server   │ │
│    │  Claude/LLM │   tool call     │  processes    │ │
│    │             │ ◄────────────── │  the request  │ │
│    └─────────────┘   tool result   └──────────────┘ │
│          │                                           │
│          ▼                                           │
│  OUTPUT: AI responds with tool result to user        │
│          e.g., file contents, HTML, JSON data         │
└─────────────────────────────────────────────────────┘
```

---

## 📌 4. MCP ARCHITECTURE & KEY CONCEPTS

### The 3 Core Building Blocks

```
┌────────────────────────────────────────────────────────┐
│              MCP SERVER CAPABILITIES                    │
│                                                         │
│  1. 🔧 TOOLS    — Functions the AI can CALL             │
│     (e.g., "search_database", "read_file")              │
│                                                         │
│  2. 📄 RESOURCES — Data the AI can READ                 │
│     (e.g., file contents, API responses)                │
│                                                         │
│  3. 💬 PROMPTS  — Reusable prompt templates             │
│     (e.g., "summarize this document")                   │
└────────────────────────────────────────────────────────┘
```

---

## 📌 5. THE TWO SIDES OF MCP

```
┌─────────────────────┐         ┌─────────────────────┐
│   MCP HOST          │         │   MCP SERVER         │
│   (The AI App)      │         │   (Your Tool/Service)│
│                     │  JSON   │                      │
│   Examples:         │◄──RPC──►│   Examples:          │
│   • Claude Desktop  │         │   • File system      │
│   • Claude Code     │         │   • Database         │
│   • VS Code (Copilot│         │   • Web scraper      │
│   • Any MCP client  │         │   • Custom tools     │
│                     │         │   • HTML generators   │
└─────────────────────┘         └─────────────────────┘
```

### Terms You Must Know

| Term           | Meaning                                   | Analogy               |
| -------------- | ----------------------------------------- | --------------------- |
| **MCP Host**   | The AI application (Claude Desktop, etc.) | The computer          |
| **MCP Client** | The connector inside the host             | The USB cable         |
| **MCP Server** | Your tool/service provider                | The USB device        |
| **Tool**       | A function the server exposes             | An app on your phone  |
| **Resource**   | Read-only data the server provides        | A file on your phone  |
| **Prompt**     | A pre-built prompt template               | A saved text template |
| **Transport**  | How messages travel (stdio, HTTP)         | The wire/wireless     |

---

## 📌 6. TYPES / PROVIDERS

### Content Types MCP Can Return

```
┌──────────────────────────────────────────────────────┐
│              CONTENT TYPES                           │
│                                                       │
│  • TextContent    → Plain text / Markdown             │
│  • ImageContent   → Base64 images (PNG, JPEG)         │
│  • AudioContent   → Base64 audio                      │
│  • ResourceLink   → Link to an MCP resource           │
│  • EmbeddedResource → Inline file content             │
│  • JSON (tool output) → Structured data               │
│                                                       │
│  ⚡ HTML can be returned as TextContent               │
│     (client decides whether to render it)             │
└──────────────────────────────────────────────────────┘
```

### Transport Types

| Transport                    | How It Works                                             | Use Case         |
| ---------------------------- | -------------------------------------------------------- | ---------------- |
| **stdio**                    | Server runs as subprocess, communicates via stdin/stdout | Local tools, CLI |
| **SSE** (Server-Sent Events) | HTTP-based, server pushes events                         | Remote servers   |
| **Streamable HTTP**          | Newer HTTP transport with streaming                      | Cloud services   |

### SDK Providers (Languages)

```
┌──────────────────────────────────────────┐
│  Official MCP SDKs                       │
│                                          │
│  • TypeScript/JavaScript  (mcp-server)   │
│  • Python                 (mcp)          │
│  • Java                   (spring-ai-mcp)│
│  • C#                     (modelcontext) │
│  • Kotlin                 (kotlin-mcp)   │
│  • Ruby                   (mcp-ruby)     │
│  • Go                     (mcp-go)       │
└──────────────────────────────────────────┘
```

---

## 📌 7. HOW TO INSTALL & RUN (Python + TypeScript)

### Python Setup

```bash
# Step 1: Create project
mkdir my-mcp-server && cd my-mcp-server
python -m venv .venv
source .venv/bin/activate    # macOS/Linux
# .venv\Scripts\activate     # Windows

# Step 2: Install MCP SDK
pip install "mcp[cli]"

# Step 3: Install FastMCP (recommended for beginners)
pip install fastmcp
```

### TypeScript Setup

```bash
# Step 1: Create project
mkdir my-mcp-server && cd my-mcp-server
npm init -y

# Step 2: Install MCP SDK
npm install @modelcontextprotocol/sdk zod

# Step 3: Install dev dependencies
npm install -D typescript @types/node
npx tsc --init
```

---

## 📌 8. MINIMAL WORKING EXAMPLE

### Python — FastMCP (Simplest!)

```python
# server.py
from fastmcp import FastMCP

# Create MCP server instance
mcp = FastMCP("My First Server")

# Define a tool — this is what the AI can call
@mcp.tool()
def greet(name: str) -> str:
    """Greet a person by name."""
    return f"Hello, {name}! Welcome to MCP! 🎉"

# Run the server via stdio
if __name__ == "__main__":
    mcp.run()
```

### TypeScript — SDK

```typescript
// server.ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Create server instance
const server = new McpServer({
  name: "my-first-server",
  version: "1.0.0",
});

// Register a tool
server.tool(
  "greet", // tool name
  "Greet a person by name", // description
  { name: z.string() }, // input schema (Zod)
  async ({ name }) => ({
    // handler function
    content: [{ type: "text", text: `Hello, ${name}! 🎉` }],
  }),
);

// Connect and run
const transport = new StdioServerTransport();
await server.connect(transport);
console.error("MCP server running on stdio");
```

### Run It

```bash
# Python
python server.py

# TypeScript (after compiling with tsc)
node dist/server.js
```

---

## 📌 9. CODE EXPLANATION FORMAT

```
┌──────────────────────────────────────────────────┐
│           HOW TO READ MCP CODE                   │
│                                                   │
│  1. CREATE  → Instantiate the server              │
│  2. DEFINE  → Register tools/resources/prompts    │
│  3. CONNECT → Attach a transport (stdio/HTTP)     │
│  4. RUN     → Start listening for requests        │
│                                                   │
│  Every MCP server follows this pattern:           │
│                                                   │
│  Server Creation                                   │
│       │                                           │
│       ▼                                           │
│  Tool/Resource Registration                       │
│       │                                           │
│       ▼                                           │
│  Transport Connection                             │
│       │                                           │
│       ▼                                           │
│  Server Running & Listening                       │
└──────────────────────────────────────────────────┘
```

---

## 📌 10. MCP WORKFLOW (End-to-End)

```
USER: "What's the weather in Tokyo?"

  ┌──────┐   1. User message   ┌──────────┐
  │ User │ ──────────────────► │ AI Host   │
  └──────┘                     │(Claude)   │
                               └────┬──────┘
                                    │ 2. AI decides to call tool
                                    ▼
                               ┌──────────┐
                               │ MCP      │  3. JSON-RPC request
                               │ Client   │ ────────────────────►┌─────────┐
                               └──────────┘                      │  MCP    │
                                    ▲                            │  Server │
                                    │ 4. Tool result (JSON)      │(weather)│
                                    │ ◄──────────────────────────└─────────┘
                                    │
                                    ▼
                               ┌──────────┐
                               │ AI Host  │  5. AI formats response
                               └────┬─────┘
                                    │
                                    ▼
  ┌──────┐   6. Final answer    ┌──────┐
  │ User │ ◄─────────────────── │ AI   │
  └──────┘                      └──────┘
```

---

## 🎯 Your First Challenge!

Before we move on to **interactive HTML output**, answer this:

> **Question:** In the Python FastMCP example above, if I add this tool:
>
> ```python
> @mcp.tool()
> def calculate(expression: str) -> str:
>     """Evaluate a math expression."""
>     result = eval(expression)
>     return str(result)
> ```
>
> **A)** What would the AI see when it discovers this tool? (What metadata is available?)
>
> **B)** If a user says _"What is 15 × 23?"_, describe the **exact sequence of messages** exchanged between the AI client and your MCP server — from tool discovery to final response.
>
> **C)** What is a potential security issue with this tool, and how would you fix it?

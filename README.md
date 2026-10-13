MCP-USE Setup Guide
********\********* use python 3.11+ version ********\*\********* This guide will help you set up and configure the mcp-use repository for use with Groq and Cursor.

🔧 Setup Instructions

1. Clone the Repository
   Use the following command to clone the repo:
   git clone https://github.com/mcp-use/mcp-use.git

2. Create a Virtual Environment
   Set up a Python virtual environment in your project directory:
   python -m venv venv
   source venv/bin/activate # On Windows use: venv\Scripts\activate

3. Switched from OpenAI to Groq
   To support Groq, a few edits have been made in the codebase replacing OpenAI-specific usage with Groq for added flexibility.

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

# MCP-USE Setup Guide
***************** use python 3.11+ version  ******************
This guide will help you set up and configure the [mcp-use](https://github.com/pietrozullo/mcp-use) repository for use with **local Ollama** and **Cursor**.

---

## 🔧 Setup Instructions

### 1. Clone the Repository  
Use the following command to clone the repo:

```bash
git clone https://github.com/mcp-use/mcp-use.git
```

---

### 2. Create a Virtual Environment  
Set up a Python virtual environment in your project directory:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

---

### 3. Use the Local Ollama Model
Demo scripts use Ollama locally by default. Configure `OLLAMA_BASE_URL` and `FREE_LLM_MODEL` in `.env` if needed.

---

### 4. Locate the Example Config File  
Inside the `Demo` folder, you'll find various configuration files. Choose the appropriate one based on your use case.

---

### 5. Add Config to Cursor Settings  
Take the selected config (e.g., `examples/browser_mcp.json`) and paste its content into **Cursor's MCP Settings**.

> 📌 Example configuration from `examples/browser_mcp.json`:

```json
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
```

Paste this in Cursor settings under the MCP section:

![Cursor Connection](image.png)

Example:

![Example Setting](image-1.png)

OUTPUT :
![alt text](image-2.png)
---

## Run the Web UI in GitHub Codespaces

From the `MCP Agentic AI` directory, start the app with:

```bash
python3 web_app.py
```

Open forwarded port **1455** in the Codespaces Ports tab.

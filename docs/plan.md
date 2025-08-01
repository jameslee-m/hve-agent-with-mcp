# Objective

Create a terminal chatbot with Azure OpenAI integration that can classify PDFs using a custom tool exposed via an MCP server.

## Architecture decisions

- Tech Stack: Python, FastMCP, Semantic Kernel

### Example Directory Structure

```
/root/
├── src/
│   ├── mcp_server/              # FastMCP server + custom PDF classification tools
│   │   ├── tools/
│   │   │   └── classify_pdf.py  # Tool that calls external REST APIs found in `samples/http/classifier-example.http`
│   │   ├── server.py            # FastAPI + FastMCP setup
│   │   └── config.yaml          # Tool registration
│   │
│   ├── chat_agent/              # Semantic Kernel + LLM agent
│   │   ├── kernel_setup.py      # Loads skills, connectors, etc.
│   │   └── agent.py             # Main chat loop
│   │
│   └── shared/                  # Shared utils (e.g., PDF parsing, logging)
│
├── data/                        # Sample documents
├── docs/                        # Documentation and plans
├── samples/                     # HTTP examples and samples
├── README.md
├── Makefile                     # Simple makefile for common commands
└── pyproject.toml
```

### MCP Server

- MCP server should ONLY have tools that correspond to the endpoints found in `samples/http/classifier-example.http`
- Use the endpoints to classify the documents. Do not use other libraries.
- For response formats look for Content Understanding Documentation in Microsoft Docs.
- Additionally, the server also should have a tool that can list the sample documents found in `data/`.
- Use the FastMCP framework to create the MCP server
- create in `src/mcp_server/`

### Chatbot

- The simple chatbot should use semantic kernel for implementation.
- The chatbot should be a generic chat assistant with good logging
- It's knowledge of external tools is determined by what's contained in the MCP server
- Do not list specific tools in the system message directly
- It will select which tool to use depending on the user queries

### Python

- when running `python` commands make sure to use `uv run` or make sure the correct environment is active
- use the environment variables found in `.env`
- keep things pythonic and simple
- use absolute imports
- use ruff for linting and formatting
- since `src` contains the actual app code, be sure to specify that in the build-system related section of the`pyproject.toml`.
- avoid adding to the PATH in code

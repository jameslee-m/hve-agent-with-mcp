# HVE Agent with MCP

A terminal chatbot with Azure OpenAI integration that can classify PDF documents using a custom tool exposed via an MCP (Model Context Protocol) server.

## Architecture

This application consists of two main components:

1. **MCP Server** (`src/mcp_server/`): FastMCP server that exposes PDF classification tools using Azure AI Service endpoints
2. **Chat Agent** (`src/chat_agent/`): Semantic Kernel-based chatbot that dynamically discovers and uses MCP tools

## Features

- 🤖 **Smart Chat Interface**: Terminal-based chat with Rich formatting
- 📄 **PDF Classification**: Classify documents using Azure AI Service endpoints
- 🔧 **Dynamic Tool Discovery**: Chat agent automatically discovers available MCP tools
- 📋 **Document Management**: List and manage sample PDF documents
- 🎯 **Classifier Management**: View and manage Azure AI classifiers
- 🧪 **Comprehensive Testing**: Unit and integration tests included

## Prerequisites

- Python 3.12+
- Azure OpenAI subscription with deployed model
- Azure AI Services with Document Intelligence capabilities
- UV package manager (or use pip/conda)

## Installation

1. Clone the repository:
```bash
git clone <repository_url>
cd hve-agent-with-mcp
```

2. Install dependencies:
```bash
make install
# or manually: uv sync --extra dev
```

3. Set up environment variables by creating a `.env` file:
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/openai/deployments/your-deployment/chat/completions?api-version=2025-01-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2025-01-01-preview

# Azure AI Service Configuration
AZURE_AI_SERVICE_ENDPOINT=https://your-ai-service.cognitiveservices.azure.com
AZURE_AI_SERVICE_KEY=your_azure_ai_service_key
```

## Usage

### Running the Chat Agent

```bash
make run
# or manually: uv run python main.py
```

This starts the interactive terminal chat interface. Example interactions:

```
You: What documents are available?
Assistant: Available sample documents:
- lease-agreement-01.pdf
- lease-agreement-02.pdf
- lease-agreement-03.pdf
- research-paper-01.pdf
- research-paper-02.pdf
- research-paper-03.pdf

You: Classify lease-agreement-01.pdf
Assistant: Document 'lease-agreement-01.pdf' classified as 'lease' with confidence 0.95

You: Show me information about the classifier
Assistant: Classifier: test-classifer-lease-02
Status: ready
Description: Test classifier for lease documents

You: help
[Shows help information]

You: quit
[Exits the application]
```

### Available Chat Commands

- **Document Operations**:
  - "What documents are available?" / "List documents"
  - "Classify [document_name]"
  
- **Classifier Operations**:
  - "Show me information about the classifier"
  - "List all classifiers"
  
- **System Commands**:
  - `help` - Show help information
  - `quit` / `exit` - Exit the application

### Running the MCP Server Standalone

```bash
make run-mcp-server
# or manually: uv run python -m src.mcp_server.server
```

### Development Commands

```bash
# Run tests
make test

# Test MCP functionality
make test-mcp

# Run integration tests
uv run python test_integration.py

# Lint code
make lint

# Format code
make format

# Clean up generated files
make clean
```

## Project Structure

```
hve-agent-with-mcp/
├── src/
│   ├── mcp_server/           # FastMCP server + custom PDF classification tools
│   │   ├── tools/
│   │   │   └── classify_pdf.py    # Azure AI Service integration
│   │   └── server.py              # FastAPI + FastMCP setup
│   ├── chat_agent/          # Semantic Kernel + LLM agent
│   │   ├── kernel_setup.py        # Loads skills, connectors, etc.
│   │   └── agent.py               # Main chat loop
│   └── shared/              # Shared utils (PDF parsing, logging, env)
├── data/                    # Sample PDF documents
├── tests/                   # Unit and integration tests
├── docs/                    # Documentation
├── main.py                  # Main entry point
├── Makefile                 # Common commands
└── pyproject.toml          # Project configuration
```

## MCP Tools

The MCP server exposes the following tools:

1. **classify_pdf**: Classify a PDF document using Azure AI Service
2. **list_sample_documents**: List all available sample PDF documents
3. **get_classifier_info**: Get information about a specific classifier
4. **list_all_classifiers**: List all available classifiers

These tools correspond to the Azure AI Service endpoints defined in `samples/http/classifier-example.http`.

## Testing

The project includes comprehensive testing:

- **Unit Tests**: Test individual components (`tests/`)
- **MCP Tests**: Test MCP server functionality (`test_mcp.py`)
- **Integration Tests**: Test full chat agent functionality (`test_integration.py`)

Run all tests:
```bash
make test
```

## Development

The project follows Python best practices:

- **Type Hints**: Comprehensive type annotations
- **Async/Await**: Proper async programming patterns
- **Error Handling**: Robust error handling and logging
- **Code Quality**: Ruff for linting and formatting
- **Modular Design**: Clean separation of concerns

## Troubleshooting

### Common Issues

1. **Environment Variables**: Ensure all required environment variables are set in `.env`
2. **Azure Permissions**: Verify your Azure OpenAI and AI Services credentials have proper permissions
3. **Network Issues**: Check firewall settings if connection to Azure services fails
4. **Dependencies**: Run `make install` to ensure all dependencies are installed

### Debug Mode

Enable debug logging by setting the log level in `src/shared/__init__.py`:

```python
logger = setup_logging("DEBUG")  # Change from "INFO" to "DEBUG"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run `make lint` and `make test`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
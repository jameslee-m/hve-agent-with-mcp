.PHONY: help install lint format test clean run run-mcp-server

# Default target
help:
	@echo "Available commands:"
	@echo "  install          - Install dependencies using uv"
	@echo "  lint             - Run ruff linter"
	@echo "  format           - Format code with ruff"
	@echo "  test             - Run tests"
	@echo "  clean            - Clean up generated files"
	@echo "  run              - Run the chat agent"
	@echo "  run-mcp-server   - Run the MCP server standalone"
	@echo "  test-mcp         - Test MCP server functionality"

# Install dependencies
install:
	uv sync

# Lint code
lint:
	uv run ruff check src/

# Format code
format:
	uv run ruff format src/

# Run tests
test:
	uv run pytest tests/

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

# Run the chat agent
run:
	uv run python main.py

# Run MCP server standalone
run-mcp-server:
	uv run python -m src.mcp_server.server

# Test MCP server functionality
test-mcp:
	uv run python test_mcp.py

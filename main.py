#!/usr/bin/env python3
"""Main entry point for the HVE Agent with MCP application."""

import asyncio
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.chat_agent.agent import main

if __name__ == "__main__":
    asyncio.run(main())

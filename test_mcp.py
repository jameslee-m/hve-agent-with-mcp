"""Test script for MCP server functionality."""

import asyncio
import logging

from src.mcp_server.tools.classify_pdf import list_documents_tool, list_classifiers_tool
from src.shared import setup_logging

async def test_mcp_tools():
    """Test the MCP server tools."""
    logger = setup_logging("DEBUG")
    
    try:
        # Test listing documents
        logger.info("Testing list_documents_tool...")
        documents = await list_documents_tool()
        logger.info(f"Found documents: {documents}")
        
        # Test listing classifiers
        logger.info("Testing list_classifiers_tool...")
        classifiers = await list_classifiers_tool()
        logger.info(f"Found classifiers: {len(classifiers)} items")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_tools())
    print(f"Test {'passed' if success else 'failed'}")

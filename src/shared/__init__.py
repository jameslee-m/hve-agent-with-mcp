"""Shared utilities for the HVE Agent application."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    return logging.getLogger(__name__)


def load_environment() -> dict:
    """Load environment variables from .env file.
    
    Returns:
        Dictionary of environment variables
    """
    load_dotenv()
    
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_AI_SERVICE_ENDPOINT",
        "AZURE_AI_SERVICE_KEY"
    ]
    
    env_vars = {}
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            env_vars[var] = value
        else:
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    return env_vars


def get_data_directory() -> Path:
    """Get the path to the data directory.
    
    Returns:
        Path to the data directory
    """
    return Path(__file__).parent.parent.parent / "data"


def list_sample_documents() -> list[str]:
    """List all sample documents in the data directory.
    
    Returns:
        List of document filenames
    """
    data_dir = get_data_directory()
    if not data_dir.exists():
        return []
    
    return [f.name for f in data_dir.glob("*.pdf")]


def get_document_path(filename: str) -> Path:
    """Get the full path to a document.
    
    Args:
        filename: Name of the document file
        
    Returns:
        Full path to the document
        
    Raises:
        FileNotFoundError: If the document doesn't exist
    """
    data_dir = get_data_directory()
    doc_path = data_dir / filename
    
    if not doc_path.exists():
        raise FileNotFoundError(f"Document not found: {filename}")
    
    return doc_path

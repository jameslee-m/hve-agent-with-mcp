"""Tests for the shared utilities module."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.shared import (
    get_data_directory,
    get_document_path,
    list_sample_documents,
    load_environment,
    setup_logging,
)


def test_setup_logging():
    """Test logging setup."""
    logger = setup_logging("DEBUG")
    assert logger is not None
    assert logger.name == "src.shared"


@patch.dict(os.environ, {
    "AZURE_OPENAI_API_KEY": "test_key",
    "AZURE_OPENAI_ENDPOINT": "test_endpoint",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "test_deployment",
    "AZURE_AI_SERVICE_ENDPOINT": "test_ai_endpoint",
    "AZURE_AI_SERVICE_KEY": "test_ai_key"
})
def test_load_environment():
    """Test environment loading."""
    env_vars = load_environment()
    
    assert "AZURE_OPENAI_API_KEY" in env_vars
    assert env_vars["AZURE_OPENAI_API_KEY"] == "test_key"
    assert "AZURE_OPENAI_ENDPOINT" in env_vars
    assert "AZURE_AI_SERVICE_ENDPOINT" in env_vars


def test_load_environment_missing_vars():
    """Test environment loading with missing variables."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="Missing required environment variables"):
            load_environment()


def test_get_data_directory():
    """Test getting data directory path."""
    data_dir = get_data_directory()
    assert isinstance(data_dir, Path)
    assert data_dir.name == "data"


def test_list_sample_documents():
    """Test listing sample documents."""
    documents = list_sample_documents()
    assert isinstance(documents, list)
    # Should have some PDF files based on our test data
    assert any(doc.endswith(".pdf") for doc in documents)


def test_get_document_path_existing():
    """Test getting document path for existing file."""
    documents = list_sample_documents()
    if documents:
        doc_path = get_document_path(documents[0])
        assert isinstance(doc_path, Path)
        assert doc_path.exists()
        assert doc_path.name == documents[0]


def test_get_document_path_nonexistent():
    """Test getting document path for non-existent file."""
    with pytest.raises(FileNotFoundError):
        get_document_path("nonexistent.pdf")

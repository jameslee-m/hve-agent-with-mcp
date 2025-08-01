"""Tests for MCP server tools."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from src.mcp_server.tools.classify_pdf import (
    AzureAIClassifier,
    classify_pdf_tool,
    list_documents_tool,
)


@pytest.mark.asyncio
async def test_list_documents_tool():
    """Test the list documents tool."""
    documents = await list_documents_tool()
    assert isinstance(documents, list)
    assert all(doc.endswith(".pdf") for doc in documents)


@pytest.mark.asyncio
@patch("src.mcp_server.tools.classify_pdf.AzureAIClassifier")
async def test_classify_pdf_tool_success(mock_classifier_class):
    """Test successful PDF classification."""
    # Mock the classifier instance
    mock_classifier = AsyncMock()
    mock_classifier.classify_document_and_wait.return_value = AsyncMock(
        operation_id="test-op-123",
        status="succeeded",
        result={
            "analyzeResult": {
                "documents": [
                    {
                        "docType": "lease",
                        "confidence": 0.95
                    }
                ]
            }
        },
        error=None
    )
    mock_classifier.classify_document_and_wait.return_value.model_dump.return_value = {
        "operation_id": "test-op-123",
        "status": "succeeded",
        "result": {
            "analyzeResult": {
                "documents": [
                    {
                        "docType": "lease",
                        "confidence": 0.95
                    }
                ]
            }
        },
        "error": None
    }
    
    mock_classifier_class.return_value = mock_classifier
    
    result = await classify_pdf_tool("test.pdf")
    
    assert result["status"] == "succeeded"
    assert result["operation_id"] == "test-op-123"
    mock_classifier.classify_document_and_wait.assert_called_once_with("test.pdf", None)


@pytest.mark.asyncio
@patch("src.mcp_server.tools.classify_pdf.AzureAIClassifier")
async def test_classify_pdf_tool_error(mock_classifier_class):
    """Test PDF classification with error."""
    # Mock the classifier instance
    mock_classifier = AsyncMock()
    mock_classifier.classify_document_and_wait.return_value = AsyncMock(
        operation_id="test-op-123",
        status="error",
        result=None,
        error="Test error"
    )
    mock_classifier.classify_document_and_wait.return_value.model_dump.return_value = {
        "operation_id": "test-op-123",
        "status": "error",
        "result": None,
        "error": "Test error"
    }
    
    mock_classifier_class.return_value = mock_classifier
    
    result = await classify_pdf_tool("test.pdf")
    
    assert result["status"] == "error"
    assert result["error"] == "Test error"


class TestAzureAIClassifier:
    """Test cases for AzureAIClassifier."""
    
    @patch("src.mcp_server.tools.classify_pdf.load_environment")
    def test_init(self, mock_load_env):
        """Test classifier initialization."""
        mock_load_env.return_value = {
            "AZURE_AI_SERVICE_ENDPOINT": "https://test.endpoint.com",
            "AZURE_AI_SERVICE_KEY": "test-key"
        }
        
        classifier = AzureAIClassifier()
        
        assert classifier.endpoint == "https://test.endpoint.com"
        assert classifier.api_key == "test-key"
        assert classifier.api_version == "2025-05-01-preview"
        assert classifier.classifier_id == "test-classifer-lease-02"
    
    @pytest.mark.asyncio
    @patch("src.mcp_server.tools.classify_pdf.load_environment")
    @patch("httpx.AsyncClient")
    async def test_get_classifier_success(self, mock_client_class, mock_load_env):
        """Test successful classifier retrieval."""
        mock_load_env.return_value = {
            "AZURE_AI_SERVICE_ENDPOINT": "https://test.endpoint.com",
            "AZURE_AI_SERVICE_KEY": "test-key"
        }
        
        mock_response = AsyncMock()
        mock_response.json.return_value = {"classifierId": "test-classifier", "status": "ready"}
        mock_response.raise_for_status.return_value = None
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client
        
        classifier = AzureAIClassifier()
        result = await classifier.get_classifier()
        
        assert result["classifierId"] == "test-classifier"
        assert result["status"] == "ready"

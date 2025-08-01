"""PDF classification tool using Azure AI Service endpoints."""

import asyncio
import logging
from pathlib import Path

import httpx
from pydantic import BaseModel

from src.shared import get_document_path, list_sample_documents, load_environment

logger = logging.getLogger(__name__)


class ClassificationRequest(BaseModel):
    """Request model for PDF classification."""
    document_path: str
    classifier_id: str = "test-classifer-lease-02"


class ClassificationResult(BaseModel):
    """Result model for PDF classification."""
    operation_id: str
    status: str
    result: dict | None = None
    error: str | None = None


class AzureAIClassifier:
    """Azure AI Service classifier client."""
    
    def __init__(self):
        """Initialize the classifier with environment variables."""
        self.env_vars = load_environment()
        self.endpoint = self.env_vars["AZURE_AI_SERVICE_ENDPOINT"]
        self.api_key = self.env_vars["AZURE_AI_SERVICE_KEY"]
        self.api_version = "2025-05-01-preview"
        self.classifier_id = "test-classifer-lease-02"
        
    async def get_classifier(self, classifier_id: str | None = None) -> dict:
        """Get a specific classifier.
        
        Args:
            classifier_id: ID of the classifier to retrieve
            
        Returns:
            Classifier information
        """
        classifier_id = classifier_id or self.classifier_id
        url = f"{self.endpoint}/contentunderstanding/classifiers/{classifier_id}"
        
        params = {"api-version": self.api_version}
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def list_classifiers(self) -> list[dict]:
        """List all classifiers.
        
        Returns:
            List of all classifiers
        """
        url = f"{self.endpoint}/contentunderstanding/classifiers"
        
        params = {"api-version": self.api_version}
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def delete_classifier(self, classifier_id: str | None = None) -> bool:
        """Delete a classifier.
        
        Args:
            classifier_id: ID of the classifier to delete
            
        Returns:
            True if deletion was successful
        """
        classifier_id = classifier_id or self.classifier_id
        url = f"{self.endpoint}/contentunderstanding/classifiers/{classifier_id}"
        
        params = {"api-version": self.api_version}
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, params=params, headers=headers)
            response.raise_for_status()
            return True
    
    async def classify_document(self, document_path: str, classifier_id: str | None = None) -> str:
        """Submit a document for classification.
        
        Args:
            document_path: Path to the PDF document
            classifier_id: ID of the classifier to use
            
        Returns:
            Operation location URL for checking status
        """
        classifier_id = classifier_id or self.classifier_id
        url = f"{self.endpoint}/contentunderstanding/classifiers/{classifier_id}:classify"
        
        params = {"api-version": self.api_version}
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/octet-stream"
        }
        
        # Get the actual file path
        if not Path(document_path).is_absolute():
            file_path = get_document_path(document_path)
        else:
            file_path = Path(document_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {document_path}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(file_path, "rb") as f:
                response = await client.post(
                    url, 
                    params=params, 
                    headers=headers, 
                    content=f.read()
                )
            response.raise_for_status()
            
            # Get operation location from headers
            operation_location = response.headers.get("Operation-Location")
            if not operation_location:
                raise ValueError("No Operation-Location header in response")
            
            return operation_location
    
    async def get_classification_result(self, operation_location: str) -> dict:
        """Get the classification result from an operation.
        
        Args:
            operation_location: URL of the operation to check
            
        Returns:
            Classification result
        """
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(operation_location, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def classify_document_and_wait(
        self, 
        document_path: str, 
        classifier_id: str | None = None,
        max_wait_time: int = 60,
        poll_interval: int = 2
    ) -> ClassificationResult:
        """Classify a document and wait for the result.
        
        Args:
            document_path: Path to the PDF document
            classifier_id: ID of the classifier to use
            max_wait_time: Maximum time to wait for result in seconds
            poll_interval: Time between polls in seconds
            
        Returns:
            Classification result
        """
        try:
            # Submit classification request
            operation_location = await self.classify_document(document_path, classifier_id)
            operation_id = operation_location.split("/")[-1]
            
            logger.info(f"Started classification for {document_path}, operation: {operation_id}")
            
            # Poll for result
            elapsed_time = 0
            while elapsed_time < max_wait_time:
                result = await self.get_classification_result(operation_location)
                status = result.get("status", "unknown").lower()
                
                logger.debug(f"Classification status: {status}")
                
                if status == "succeeded":
                    return ClassificationResult(
                        operation_id=operation_id,
                        status=status,
                        result=result
                    )
                elif status == "failed":
                    error_msg = result.get("error", {}).get("message", "Classification failed")
                    return ClassificationResult(
                        operation_id=operation_id,
                        status=status,
                        error=error_msg
                    )
                elif status in ["running", "notStarted"]:
                    # Continue polling - don't return early
                    await asyncio.sleep(poll_interval)
                    elapsed_time += poll_interval
                else:
                    return ClassificationResult(
                        operation_id=operation_id,
                        status=status,
                        error=f"Unknown status: {status}"
                    )
            
            # If we get here, we've timed out
            return ClassificationResult(
                operation_id=operation_id,
                status="timeout",
                error=f"Classification timed out after {max_wait_time} seconds"
            )
            
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            return ClassificationResult(
                operation_id="unknown",
                status="error",
                error=str(e)
            )


async def classify_pdf_tool(document_name: str, classifier_id: str | None = None) -> dict:
    """Tool function to classify a PDF document.
    
    Args:
        document_name: Name of the document to classify
        classifier_id: Optional classifier ID to use
        
    Returns:
        Classification result as dictionary
    """
    classifier = AzureAIClassifier()
    # Increase wait time and polling frequency for better results
    result = await classifier.classify_document_and_wait(
        document_name, 
        classifier_id,
        max_wait_time=120,  # Increased from 60 to 120 seconds
        poll_interval=3     # Increased from 2 to 3 seconds to be less aggressive
    )
    return result.model_dump()


async def list_documents_tool() -> list[str]:
    """Tool function to list available sample documents.
    
    Returns:
        List of available document names
    """
    return list_sample_documents()


async def get_classifier_info_tool(classifier_id: str | None = None) -> dict:
    """Tool function to get classifier information.
    
    Args:
        classifier_id: Optional classifier ID to get info for
        
    Returns:
        Classifier information
    """
    classifier = AzureAIClassifier()
    return await classifier.get_classifier(classifier_id)


async def list_classifiers_tool() -> list[dict]:
    """Tool function to list all classifiers.
    
    Returns:
        List of all classifiers
    """
    classifier = AzureAIClassifier()
    return await classifier.list_classifiers()

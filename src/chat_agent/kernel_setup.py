"""Semantic Kernel setup and configuration."""

import logging
import json

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
)
from semantic_kernel.functions.kernel_function_decorator import kernel_function

from src.shared import load_environment, setup_logging

logger = setup_logging()


class MCPConnector:
    """Connector to integrate MCP tools with Semantic Kernel."""
    
    def __init__(self):
        """Initialize the MCP connector."""
        self.logger = logging.getLogger(__name__)
        
    @kernel_function(
        description="Classify a PDF document using Azure AI Service",
        name="classify_pdf"
    )
    async def classify_pdf(self, document_name: str, classifier_id: str | None = None) -> str:
        """Classify a PDF document.
        
        Args:
            document_name: Name of the PDF document to classify
            classifier_id: Optional classifier ID to use
            
        Returns:
            Classification result as JSON string
        """
        from src.mcp_server.tools.classify_pdf import classify_pdf_tool
        
        self.logger.info(f"Classifying document: {document_name}")
        result = await classify_pdf_tool(document_name, classifier_id)
        
        # Format result for the chat agent
        if result.get("status") == "succeeded":
            classification_result = result.get("result", {})
            
            # Azure AI Service returns nested result structure
            inner_result = classification_result.get("result", {})
            contents = inner_result.get("contents", [])
            
            if contents:
                # Get the first content item (document classification)
                content = contents[0]
                category = content.get("category", "unknown")
                page_range = f"pages {content.get('startPageNumber', 1)}-{content.get('endPageNumber', '?')}"
                
                return f"Document '{document_name}' classified as '{category}' ({page_range})"
            else:
                return f"Document '{document_name}' could not be classified - no classification results found"
        elif result.get("status") == "error":
            error_msg = result.get("error", "Unknown error")
            return f"Error classifying document '{document_name}': {error_msg}"
        elif result.get("status") == "timeout":
            return f"Classification of document '{document_name}' timed out"
        else:
            # For any other status, return an error to avoid incomplete responses
            status = result.get("status", "unknown")
            error_msg = result.get("error", f"Unexpected status: {status}")
            return f"Classification of document '{document_name}' failed: {error_msg}"
    
    @kernel_function(
        description="List all available sample PDF documents",
        name="list_documents"
    )
    async def list_documents(self) -> str:
        """List available sample documents.
        
        Returns:
            List of available documents as string
        """
        from src.mcp_server.tools.classify_pdf import list_documents_tool
        
        self.logger.info("Listing sample documents")
        documents = await list_documents_tool()
        
        if documents:
            doc_list = "\n".join(f"- {doc}" for doc in documents)
            return f"Available sample documents:\n{doc_list}"
        else:
            return "No sample documents found."
    
    @kernel_function(
        description="Get information about available classifiers",
        name="get_classifier_info"
    )
    async def get_classifier_info(self, classifier_id: str | None = None) -> str:
        """Get classifier information.
        
        Args:
            classifier_id: Optional classifier ID to get info for
            
        Returns:
            Classifier information as string
        """
        from src.mcp_server.tools.classify_pdf import get_classifier_info_tool
        
        self.logger.info(f"Getting classifier info for: {classifier_id or 'default'}")
        
        try:
            info = await get_classifier_info_tool(classifier_id)
            
            # Extract basic information
            classifier_name = info.get("classifierId", "unknown")
            status = info.get("status", "unknown")
            description = info.get("description", "No description available")
            created_date = info.get("createdDateTime", "unknown")
            api_version = info.get("apiVersion", "unknown")
            
            # Build detailed information string
            result_parts = [
                f"📋 Classifier Details",
                f"• ID: {classifier_name}",
                f"• Status: {status}",
                f"• Description: {description}",
                f"• Created: {created_date}",
                f"• API Version: {api_version}"
            ]
            
            # Add document classes if available
            doc_types = info.get("docTypes", {})
            if doc_types:
                result_parts.append(f"\n📝 Document Types:")
                for doc_type_name, doc_type_info in doc_types.items():
                    confidence_threshold = doc_type_info.get("confidenceThreshold", "N/A")
                    result_parts.append(f"• {doc_type_name} (confidence threshold: {confidence_threshold})")
            
            return json.dumps(info)
        except Exception as e:
            return f"Error getting classifier info: {str(e)}"
    
    @kernel_function(
        description="List all available classifiers",
        name="list_classifiers"
    )
    async def list_classifiers(self) -> str:
        """List all available classifiers.
        
        Returns:
            List of classifiers as string
        """
        from src.mcp_server.tools.classify_pdf import list_classifiers_tool
        
        self.logger.info("Listing all classifiers")
        
        try:
            classifiers = await list_classifiers_tool()
            
            # Handle different response formats
            classifiers_list = []
            if isinstance(classifiers, dict) and "value" in classifiers:
                classifiers_list = classifiers.get("value", [])
            elif isinstance(classifiers, list):
                classifiers_list = classifiers
            
            if classifiers_list:
                classifier_info = []
                for classifier in classifiers_list:
                    if isinstance(classifier, dict):
                        name = classifier.get("classifierId", "unknown")
                        status = classifier.get("status", "unknown")
                        classifier_info.append(f"- {name} (status: {status})")
                
                if classifier_info:
                    return "Available classifiers:\n" + "\n".join(classifier_info)
                else:
                    return "No classifiers found in response."
            else:
                return "No classifiers available."
        except Exception as e:
            return f"Error listing classifiers: {str(e)}"


def create_kernel() -> Kernel:
    """Create and configure a Semantic Kernel instance.
    
    Returns:
        Configured Kernel instance
    """
    env_vars = load_environment()
    
    # Create kernel
    kernel = Kernel()
    
    # Extract base endpoint from the full endpoint URL
    full_endpoint = env_vars["AZURE_OPENAI_ENDPOINT"]
    if "/openai/" in full_endpoint:
        base_endpoint = full_endpoint.split("/openai/")[0]
    else:
        base_endpoint = full_endpoint
    
    # Add Azure OpenAI chat completion service
    chat_service = AzureChatCompletion(
        deployment_name=env_vars["AZURE_OPENAI_DEPLOYMENT_NAME"],
        endpoint=base_endpoint,
        api_key=env_vars["AZURE_OPENAI_API_KEY"],
        api_version=env_vars["AZURE_OPENAI_API_VERSION"]
    )
    
    kernel.add_service(chat_service)
    
    # Add MCP connector as a plugin
    mcp_connector = MCPConnector()
    kernel.add_plugin(mcp_connector, plugin_name="mcp_tools")
    
    logger.info("Kernel created with Azure OpenAI and MCP tools")
    return kernel


def get_system_message() -> str:
    """Get the system message for the chat agent.
    
    Returns:
        System message string
    """
    return """You are an AI assistant that can help classify PDF documents using Azure AI Services.

You have access to the following tools:
- classify_pdf: Classify a PDF document using Azure AI Service
- list_documents: List all available sample PDF documents  
- get_classifier_info: Get information about a specific classifier
- list_classifiers: List all available classifiers

IMPORTANT: When using tools for document classification:
- Always wait for all tool calls to complete before responding
- If a user asks to classify multiple documents, wait for ALL classifications to finish
- Only provide a final response once you have complete results for all requested operations
- Do not provide intermediate status updates while tools are still running

When a user asks about classifying documents, first check what documents are available using list_documents.
When classifying, provide clear information about the classification results including the document type and confidence level.
Be helpful and provide context about what the classification results mean.

Always be concise but informative in your responses."""

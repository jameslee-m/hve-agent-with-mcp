"""FastMCP server for PDF classification tools."""


from fastmcp import FastMCP

from src.mcp_server.tools.classify_pdf import (
    classify_pdf_tool,
    get_classifier_info_tool,
    list_classifiers_tool,
    list_documents_tool,
)
from src.shared import setup_logging

# Setup logging
logger = setup_logging("DEBUG")

# Create FastMCP instance
mcp = FastMCP("PDF Classification Server")


@mcp.tool()
async def classify_pdf(document_name: str, classifier_id: str | None = None) -> dict:
    """Classify a PDF document using Azure AI Service.
    
    Args:
        document_name: Name of the PDF document to classify (from the data/ directory)
        classifier_id: Optional classifier ID to use (defaults to test-classifer-lease-02)
        
    Returns:
        Classification result including status, operation ID, and results
    """
    logger.info(f"Classifying document: {document_name}")
    return await classify_pdf_tool(document_name, classifier_id)


@mcp.tool()
async def list_sample_documents() -> list[str]:
    """List all available sample PDF documents.
    
    Returns:
        List of PDF document names available for classification
    """
    logger.info("Listing sample documents")
    return await list_documents_tool()


@mcp.tool()
async def get_classifier_info(classifier_id: str | None = None) -> dict:
    """Get information about a specific classifier.
    
    Args:
        classifier_id: ID of the classifier to get info for (optional)
        
    Returns:
        Classifier information including configuration and status
    """
    logger.info(f"Getting classifier info for: {classifier_id or 'default'}")
    return await get_classifier_info_tool(classifier_id)


@mcp.tool()
async def list_all_classifiers() -> list[dict]:
    """List all available classifiers.
    
    Returns:
        List of all classifiers with their information
    """
    logger.info("Listing all classifiers")
    return await list_classifiers_tool()


if __name__ == "__main__":
    # Run the server
    mcp.run()

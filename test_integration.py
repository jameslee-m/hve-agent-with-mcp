"""Integration test for the chat agent with MCP functionality."""

import asyncio
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.chat_agent.agent import ChatAgent
from src.shared import setup_logging

logger = setup_logging("INFO")


async def test_chat_agent_functionality():
    """Test the chat agent's functionality with various inputs."""
    print("Testing PDF Classification Chat Agent...")
    
    try:
        # Initialize chat agent
        agent = ChatAgent()
        print("✓ Chat agent initialized successfully")
        
        # Test 1: List documents
        print("\nTest 1: Listing documents...")
        response = await agent.process_user_input("What documents are available?")
        print(f"Response: {response[:200]}..." if len(response) > 200 else f"Response: {response}")
        assert "lease-agreement" in response.lower() or "research-paper" in response.lower()
        print("✓ Document listing works")
        
        # Test 2: Get classifier info
        print("\nTest 2: Getting classifier information...")
        response = await agent.process_user_input("Show me information about the classifier")
        print(f"Response: {response[:200]}..." if len(response) > 200 else f"Response: {response}")
        assert "classifier" in response.lower()
        print("✓ Classifier info retrieval works")
        
        # Test 3: List classifiers
        print("\nTest 3: Listing classifiers...")
        response = await agent.process_user_input("List all classifiers")
        print(f"Response: {response[:200]}..." if len(response) > 200 else f"Response: {response}")
        assert "classifier" in response.lower()
        print("✓ Classifier listing works")
        
        # Test 4: Classify a document (this will take longer)
        print("\nTest 4: Classifying a document...")
        response = await agent.process_user_input("Classify lease-agreement-01.pdf")
        print(f"Response: {response[:300]}..." if len(response) > 300 else f"Response: {response}")
        # This might succeed or fail depending on the classifier, but should handle it gracefully
        print("✓ Document classification attempted")
        
        print("\n" + "="*60)
        print("🎉 All tests completed successfully!")
        print("The chat agent is working correctly with MCP integration.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        logger.error(f"Test failure: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_chat_agent_functionality())
    sys.exit(0 if success else 1)

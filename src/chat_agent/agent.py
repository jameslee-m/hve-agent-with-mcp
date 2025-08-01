"""Main chat agent implementation."""

import asyncio

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from semantic_kernel.contents import ChatHistory

from src.chat_agent.kernel_setup import create_kernel, get_system_message
from src.shared import setup_logging

logger = setup_logging("INFO")


class ChatAgent:
    """Terminal-based chat agent with PDF classification capabilities."""
    
    def __init__(self):
        """Initialize the chat agent."""
        self.console = Console()
        self.kernel = create_kernel()
        self.chat_history = ChatHistory()
        self.system_message = get_system_message()
        
        # Add system message to history
        self.chat_history.add_system_message(self.system_message)
        
        logger.info("Chat agent initialized")
    
    async def process_user_input(self, user_input: str) -> str:
        """Process user input and generate response.
        
        Args:
            user_input: User's input message
            
        Returns:
            Agent's response
        """
        # Add user message to history
        self.chat_history.add_user_message(user_input)
        
        try:
            # Get chat completion service
            chat_service = self.kernel.get_service(type=None)
            
            # Generate response with function calling enabled
            response = await chat_service.get_chat_message_content(
                chat_history=self.chat_history,
                settings=chat_service.get_prompt_execution_settings_class()(
                    function_choice_behavior="auto"
                ),
                kernel=self.kernel
            )
            
            # Add assistant response to history
            self.chat_history.add_assistant_message(str(response))
            
            return str(response)
            
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def display_welcome(self):
        """Display welcome message."""
        welcome_text = """
# Welcome to PDF Classification Assistant

I can help you classify PDF documents using Azure AI Services. Here's what I can do:

- **List documents**: Show available sample documents
- **Classify PDFs**: Analyze document types with confidence scores
- **Get classifier info**: View classifier details and status
- **List classifiers**: Show all available classifiers

Try asking me something like:
- "What documents are available?"
- "Classify the lease-agreement-01.pdf document"
- "Show me information about the classifier"

Type 'help' for more information or 'quit' to exit.
        """
        
        self.console.print(Panel(Markdown(welcome_text), title="PDF Classification Assistant", border_style="blue"))
    
    def display_help(self):
        """Display help information."""
        help_text = """
# Available Commands

- **list documents** or **show documents**: List available PDF documents
- **classify [document_name]**: Classify a specific PDF document
- **classifier info**: Get information about the current classifier
- **list classifiers**: Show all available classifiers
- **help**: Show this help message
- **quit** or **exit**: Exit the application

# Example Queries

- "What documents can I classify?"
- "Classify lease-agreement-01.pdf"
- "Show me the classifier information"
- "What types of documents can be classified?"
        """
        
        self.console.print(Panel(Markdown(help_text), title="Help", border_style="green"))
    
    async def run(self):
        """Run the main chat loop."""
        self.display_welcome()
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold blue]You[/bold blue]").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit']:
                    self.console.print("\n[bold blue]Goodbye![/bold blue]")
                    break
                elif user_input.lower() == 'help':
                    self.display_help()
                    continue
                
                # Process user input
                self.console.print("\n[bold green]Assistant[/bold green]:", end=" ")
                
                with self.console.status("[bold green]Thinking...", spinner="dots"):
                    response = await self.process_user_input(user_input)
                
                # Display response
                self.console.print(response)
                
            except KeyboardInterrupt:
                self.console.print("\n\n[bold blue]Goodbye![/bold blue]")
                break
            except Exception as e:
                logger.error(f"Unexpected error in chat loop: {str(e)}")
                self.console.print(f"\n[bold red]Error:[/bold red] {str(e)}")


async def main():
    """Main entry point for the chat agent."""
    agent = ChatAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())

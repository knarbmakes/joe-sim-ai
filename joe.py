import logging
from dotenv import load_dotenv
from src.core.file_based_context import FileBasedContext
from src.core.tool_agent import ObjectConfig, TextConfig, ToolAgent
import chromadb

# IMPORTANT: Import all tools so registry can be populated
import src.tools.asteval
import src.tools.memory_save
import src.tools.memory_query
import src.tools.memory_delete
import src.tools.web_search
import src.tools.scrape_website
import src.tools.file_read
import src.tools.file_write
import src.tools.bash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


def main():
    # Initialize Collection for this Agent
    client = chromadb.PersistentClient(path="/tmp/chroma_db")
    collection = client.get_or_create_collection(name="coder_db")
    logging.info(f"Collection Loaded: {collection.count()} documents")

    # Initialize the Agent
    code_agent = ToolAgent(
        TextConfig(
            agent_key="coder",
            model="gpt-4-1106-preview",
            budget_dollars=2.0,
            available_functions=[
                "asteval",
                "memory_save",
                "memory_query",
                "memory_delete",
                "web_search",
                "scrape_website",
                "file_read",
                "file_write",
                "bash",
            ],
            system_message=" ".join(
                [
                    "You are a helpful assistant! You help with coding, planning, and calculations. You call memory_query any time you need to remember something.",
                    "As a self-improving AI, I continually integrate feedback to provide more accurate, relevant, and valuable assistance over time.",
                ]
            ),
            kwargs={},
        ),
        ObjectConfig(
            agent_id=f"c004",
            agent_service=FileBasedContext(),
            chroma_db_collection=collection,
        ),
    )

    # Loop for interaction
    while True:
        # Get the current running cost
        current_cost = code_agent.get_running_cost()
        logger.info(
            f"Current cost: ${current_cost:.2f} out of ${code_agent.text_config.budget_dollars:.2f}"
        )

        # Check if budget exceeded
        if current_cost >= code_agent.text_config.budget_dollars:
            user_choice = (
                input("Budget exceeded. Add more budget (Y/N) or type 'exit' to stop: ")
                .strip()
                .lower()
            )
            if user_choice == "y":
                try:
                    additional_budget = float(input("Pay down budget: $"))
                    code_agent.add_budget(additional_budget)
                except ValueError:
                    logger.error("Invalid budget amount. Please enter a numeric value.")
            elif user_choice == "exit":
                logger.info(f"Exiting...")
                break
            else:
                logger.error(
                    "Invalid input. Please enter 'Y' to add budget, or 'exit' to stop."
                )
        else:
            # Ask the user for their question/input
            user_input = input("Enter your question or command: ")

            # Check if the user wants to exit
            if user_input.lower() == "exit":
                logger.info(f"Exiting...")
                break

            logger.info(f"Thinking...")

            # Resume agent execution with the user's input
            response = code_agent.run(
                input_messages=[{"role": "user", "content": user_input}]
            )
            if response and response.get("status") == "success":
                logger.info(f"Agent response: {response.get('output')}")
            elif response and response.get("status") == "error":
                logger.error(f"Error: {response.get('error')}")
                break


if __name__ == "__main__":
    main()

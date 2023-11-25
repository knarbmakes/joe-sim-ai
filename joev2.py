import json
import logging
from dotenv import load_dotenv
from src.core.file_based_bank_account import FileBasedBankAccount
from src.core.file_based_context import FileBasedContext
from src.core.tool_agent import ObjectConfig, TextConfig, ToolAgent
from datetime import datetime
import chromadb

# IMPORTANT: Import all tools so registry can be populated
import src.tools.asteval
import src.tools.memory_save
import src.tools.memory_query
import src.tools.memory_delete
import src.tools.web_search
import src.tools.file_read
import src.tools.file_write
import src.tools.bash

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment variables from .env file
load_dotenv()

def handle_answer_agent(answer_agent, user_input, sys_message_suffix, user_name):
    logger.info(f"Running Agent...")
    response = answer_agent.run(
        input_messages=[{"role": "user", "name": user_name, "content": user_input}],
        sys_message_suffix=sys_message_suffix
    )
    if response and response.get("status") == "success":
        logger.info(f"Agent Response: {response.get('output')}")
        return response.get('output')
    return None

def handle_verification_agent(verification_agent, user_input, answer_output, sys_message_suffix=None):
    logger.info(f"Verifying answer...")
    verification_response = verification_agent.run(
        input_messages=[{"role": "user", "name": "answer_agent", "content": f"In the context of the user's request:\n{user_input}\n\nVerify the answer:\n{answer_output}"}],
        sys_message_suffix=sys_message_suffix
    )
    if verification_response and verification_response.get("status") == "success":
        # Parse the output as a JSON string
        parsed = json.loads(verification_response.get('output'))
        logger.info(f"Agent Response: {parsed}")
        return parsed
    return None

def main():
    # Initialize Collection for this Agent
    client = chromadb.PersistentClient(path="/tmp/chroma_db")
    collection = client.get_or_create_collection(name="coder_db")
    logging.info(f"Collection Loaded: {collection.count()} documents")

    # Initialize Bank Account
    bank_account = FileBasedBankAccount(account_id="ba001")

    # Initialize the Code Agent with an enhanced system message
    verbose_system_message = " ".join([
        "You are a helpful assistant that explains your reasoning in detail.",
        "For each step, you will provide a clear explanation of the logic you are applying.",
        "This will help to track your thought process and make it easier",
        "to identify where things might have gone wrong, if they do."
    ])

    answer_agent = ToolAgent(
        TextConfig(
            agent_key="answer_agent",
            model="gpt-4-1106-preview",
            available_functions=[
                "asteval",
                "memory_save",
                "memory_query",
                "memory_delete",
                "web_search",
                "file_read",
                "file_write",
                "bash",
            ],
            system_message=verbose_system_message,
            kwargs={},
        ),
        ObjectConfig(
            agent_id=f"aa001",
            agent_service=FileBasedContext(),
            bank_account=bank_account,
            chroma_db_collection=collection,
        ),
    )

    # Initialize a Verification Agent that cross-checks the Code Agent's output
    verification_agent = ToolAgent(
        TextConfig(
            agent_key="verifier",
            model="gpt-4-1106-preview",
            available_functions=[
                "asteval",
                "memory_save",
                "memory_query",
                "memory_delete",
                "web_search",
                "file_read",
                "file_write",
                "bash",
            ],
            system_message="I am a verification assistant. I will validate the reasoning and conclusions provided by the code assistant for accuracy. I output JSON responses in the format: {'revision_required': True/False, 'feedback': 'optional feedback string'}",
            kwargs={
                "response_format": {
                    "type": "json_object"
                }
            },
        ),
        ObjectConfig(
            agent_id=f"va001",
            agent_service=FileBasedContext(),
            bank_account=bank_account,
            chroma_db_collection=collection,
        ),
    )

    # Loop for interaction
    max_revisions = 3
    revision_counter = 0
    while True:
        current_balance = bank_account.get_balance()
        logging.info(f"Current balance: ${current_balance}")

        if current_balance <= 0:
            logging.info("Bank account balance depleted, exiting...")
            break

        user_input = input("Enter your question or command: ")
        if user_input.lower() == "exit":
            logging.info("Exiting...")
            break

        sys_message_suffix = f"\n\nCurrent Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nCurrent Account Balance: ${current_balance:.2f}"
        answer_output = handle_answer_agent(answer_agent, user_input, sys_message_suffix, "end_user")

        if answer_output:
            revision_counter = 0
            while revision_counter < max_revisions:
                verification_result = handle_verification_agent(verification_agent, user_input, answer_output, sys_message_suffix)
                if verification_result and verification_result.get('revision_required'):
                    revision_counter += 1
                    feedback_input = verification_result.get('feedback')
                    answer_output = handle_answer_agent(answer_agent, feedback_input, sys_message_suffix, "verifier")
                else:
                    logging.info("No revision required, verification successful.")
                    break

            if revision_counter >= max_revisions:
                logging.info("Maximum revisions reached.")

if __name__ == "__main__":
    main()

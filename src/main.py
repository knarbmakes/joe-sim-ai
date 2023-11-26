import json
import logging
import traceback
from dotenv import load_dotenv
from core.file_based_bank_account import FileBasedBankAccount
from core.file_based_context import FileBasedContext
from core.tool_agent import ObjectConfig, TextConfig, ToolAgent
from datetime import datetime
import chromadb

# IMPORTANT: Import all tools so registry can be populated
import tools.asteval
import tools.memory_save
import tools.memory_query
import tools.memory_delete
import tools.web_search
import tools.file_read
import tools.file_write
import tools.bash

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment variables from .env file
load_dotenv()


def handle_answer_agent(answer_agent, user_input, sys_message_suffix, user_name):
    logger.info(f"Running Agent...")
    response = answer_agent.run(
        input_messages=[{"role": "user", "name": user_name, "content": user_input}],
        sys_message_suffix=sys_message_suffix,
    )
    if response and response.get("status") == "success":
        logger.info(f"Agent Response: {response.get('output')}")
        return response
    return None


def handle_verification_agent(
    verification_agent, user_input, answer_output, sys_message_suffix, user_name):
    logger.info(f"Verifying answer...")
    verification_response = verification_agent.run(
        input_messages=[
            {
                "role": "user",
                "name": "answer_agent",
                "content": f"In the context of the user's request:\n{user_input}\n\nTool Execution log:\n{answer_output.get('tool_execution_log')}\n\Read the final answer and give feedback:\n{answer_output.get('output')}\n",
            }
        ],
        sys_message_suffix=sys_message_suffix,
    )
    if verification_response and verification_response.get("status") == "success":
        # Parse the output as a JSON string
        parsed = json.loads(verification_response.get("output"))
        logger.info(f"Agent Response: {parsed}")
        return parsed
    return None


def main():
    # Initialize Collection for this Agent
    client = chromadb.PersistentClient(path="memory/chroma_db")
    collection = client.get_or_create_collection(name="coder_db")
    logging.info(f"Collection Loaded: {collection.count()} documents")

    # Initialize Bank Account
    bank_account = FileBasedBankAccount(account_id="ba001", folder="memory/bank_account")

    function_list = [
        "asteval",
        "memory_save",
        "memory_query",
        "memory_delete",
        "web_search",
        "file_read",
        "file_write",
        "bash",
    ]

    answer_agent_instructions = " ".join(
        [
            "You are a helpful agent that explains your reasoning in step by step detail.",
            "For each step, you will provide a clear explanation of the logic you are applying.",
            "This will help to track your thought process and make it easier",
            "to identify where things might have gone wrong, if they do.",
            "NOTE: Together with the verifier agent, this agent has access to advanced tools such as web_search and bash and can download files from the internet and execute arbitrary code."
        ]
    )

    answer_agent = ToolAgent(
        TextConfig(
            agent_key="answer_agent",
            model="gpt-4-1106-preview",
            available_functions=function_list,
            system_message=answer_agent_instructions,
            kwargs={},
        ),
        ObjectConfig(
            agent_id=f"aa001",
            agent_service=FileBasedContext(agent_id="aa001", folder="memory/context"),
            bank_account=bank_account,
            chroma_db_collection=collection,
        ),
    )

    verification_agent_instructions = " ".join(
        [
            "You are a verification agent. You will validate the reasoning steps and conclusions provided by the answer agent for accuracy. If any revisions are required, you will provide feedback to the answer agent and set the revision_required flag to True.",
            "You also attempt to identify gaps in memory by first querying the memory database for relevant information, then inserting memories with new information (also deleting outdated memories if necessary).",
            "Other than memory alteration, you will not attempt to write files or execute mutations."
            "NOTE: Together with the answer agent, this agent has access to advanced tools such as web_search and bash and can download files from the internet and execute arbitrary code."
            "You will output JSON responses in the format: {'feedback': 'optional feedback string', 'revision_required': True/False}",
        ]
    )

    # Initialize a Verification Agent that cross-checks the Code Agent's output
    verification_agent = ToolAgent(
        TextConfig(
            agent_key="verifier",
            model="gpt-4-1106-preview",
            available_functions=function_list,
            system_message=verification_agent_instructions,
            kwargs={"response_format": {"type": "json_object"}},
        ),
        ObjectConfig(
            agent_id=f"va001",
            agent_service=FileBasedContext(agent_id="va001", folder="memory/context"),
            bank_account=bank_account,
            chroma_db_collection=collection,
        ),
    )

    # Replace the existing user input prompt
    max_revisions = 1
    revision_counter = 0
    while True:
        try:
            current_balance = bank_account.get_balance()
            logging.info(f"Current balance: ${current_balance}")

            if current_balance <= 0:
                logging.info("Bank account balance depleted, exiting...")
                break

            # Input validation loop
            while True:
                user_input = input("Enter your question or command: ").strip()  # Use .strip() to remove whitespace from the beginning and end
                if user_input:  # This checks that user_input is not an empty string
                    break
                else:
                    print("Input cannot be empty, please try again.")

            sys_message_suffix = f"\n\nCurrent Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nCurrent Account Balance: ${current_balance:.2f}"
            answer_output = handle_answer_agent(
                answer_agent, user_input, sys_message_suffix, "end_user"
            )

            if answer_output:
                revision_counter = 0
                while revision_counter < max_revisions:
                    verification_result = handle_verification_agent(
                        verification_agent, user_input, answer_output, sys_message_suffix, "answer_agent"
                    )
                    if verification_result and verification_result.get("revision_required"):
                        revision_counter += 1
                        feedback_input = verification_result.get("feedback")
                        answer_output = handle_answer_agent(
                            answer_agent, feedback_input, sys_message_suffix, "verifier"
                        )
                    else:
                        logging.info("No revision required, verification successful.")
                        break

                if revision_counter >= max_revisions:
                    logging.info("Maximum revisions reached.")
        except Exception as e:
            traceback.print_exc()
            logging.error(f"Error: {e}")


if __name__ == "__main__":
    main()

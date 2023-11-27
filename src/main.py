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


def create_agent_config(agent_config, agent_id, bank_account, memory_collection):
    text_config = TextConfig(
        agent_key=agent_config['agent_key'],
        model=agent_config['model'],
        available_functions=agent_config['available_functions'],
        system_message=agent_config['system_message'],
        kwargs=agent_config.get('kwargs', {})
    )
    object_config = ObjectConfig(
        agent_id=agent_id,
        agent_service=FileBasedContext(agent_id=agent_id, folder="memory/context"),
        bank_account=bank_account,
        chroma_db_collection=memory_collection,
    )

    return text_config, object_config


def load_agent_configs(config_json, bank_account, memory_collection):
    with open(config_json, 'r') as file:
        config = json.load(file)

    # Config for the Answer Agent
    answer_agent_config = create_agent_config(config['answer_agent'], "aa001", bank_account, memory_collection)

    # Config for the Verification Agent
    verifier_agent_config = create_agent_config(config['verifier_agent'], "va001", bank_account, memory_collection)

    return {
        "answer_agent": answer_agent_config,
        "verifier_agent": verifier_agent_config
    }


def main():
    # Initialize Collection for this Agent
    client = chromadb.PersistentClient(path="memory/chroma_db")
    memory_collection = client.get_or_create_collection(name="coder_db")
    logging.info(f"Collection Loaded: {memory_collection.count()} documents")

    # Initialize Bank Account
    bank_account = FileBasedBankAccount(account_id="ba001", folder="memory/bank_account")

    configs = load_agent_configs('agent_config.json', bank_account, memory_collection)
    answer_agent = ToolAgent(*configs['answer_agent'])
    verification_agent = ToolAgent(*configs['verifier_agent'])

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

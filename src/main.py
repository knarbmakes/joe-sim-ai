import json
import logging
import os
import traceback
import time
from dotenv import load_dotenv
from core.file_based_bank_account import FileBasedBankAccount
from core.file_based_context import FileBasedContext
from core.file_based_kanban import FileBasedKanbanBoard
from core.neo4j_client import Neo4jClient
from core.tool_agent import ObjectConfig, TextConfig, ToolAgent
from datetime import datetime
import chromadb
from typing import Any, Union

# IMPORTANT: Import all tools so registry can be populated
import tools

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment variables from .env file
load_dotenv()

def run_agent(task_agent: ToolAgent, user_name: str, user_input: Union[str, None] = None, sys_message_suffix: Union[str, None] = None) -> Union[dict[str, Any], None]:
    logger.info(f"Running Agent {task_agent.agent_key}...")
    response = task_agent.run(
        input_messages=[{"role": "user", "name": user_name, "content": user_input}] if user_input else None,
        sys_message_suffix=sys_message_suffix,
    )
    if response and response.get("status") == "success":
        logger.info(f"Agent Response: {response.get('output')}")
        return response
    return None


def create_agent_config(
    agent_config, agent_id, bank_account, memory_collection, kanban, neo4j
):
    response_format = ""
    if "response_format" in agent_config.get("kwargs", {}):
        response_format = "\n\nYou output responses in the following JSON format:\n" + json.dumps(agent_config['response_schema'], indent=2)

    text_config = TextConfig(
        agent_key=agent_config["agent_key"],
        model=agent_config["model"],
        available_functions=agent_config["available_functions"],
        system_message=agent_config["system_message"] + response_format,
        kwargs=agent_config.get("kwargs", {}),
    )
    object_config = ObjectConfig(
        agent_id=agent_id,
        agent_service=FileBasedContext(agent_id=agent_id, folder="memory/context"),
        bank_account=bank_account,
        chroma_db_collection=memory_collection,
        kanban_board=kanban,
        neo4j=neo4j,
    )

    return text_config, object_config


def load_agent_configs(config_filename, bank_account, memory_collection, kanban, neo4j):
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path to the config file
    config_path = os.path.join(script_dir, config_filename)

    with open(config_path, "r") as file:
        config = json.load(file)

    # Config for the Answer Agent
    task_agent_config = create_agent_config(
        config["task_agent"], "ta002", bank_account, memory_collection, kanban, neo4j
    )

    return {"task_agent": task_agent_config}


def main():
    # Initialize Collection for this Agent
    client = chromadb.PersistentClient(path="memory/chroma_db")
    neo4j = Neo4jClient()
    memory_collection = client.get_or_create_collection(name="coder_db")
    logging.info(f"Collection Loaded: {memory_collection.count()} documents")

    # Initialize Kanban Board
    kanban = FileBasedKanbanBoard(board_id="kb1", folder="memory/kanban")

    # Initialize Bank Account
    bank_account = FileBasedBankAccount(
        account_id="ba001", folder="memory/bank_account"
    )

    configs = load_agent_configs(
        "agent_config.json", bank_account, memory_collection, kanban, neo4j
    )

    task_agent = ToolAgent(*configs["task_agent"])

    num_errors = 0
    while True:
        try:
            current_balance = bank_account.get_balance()
            logging.info(f"Current balance: ${current_balance}")

            # Add some delay to simulate human response time
            time.sleep(0.2)

            if current_balance <= 0:
                logging.info("Bank account balance depleted, exiting...")
                break

            suffix = f"\n\nCurrent Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nCurrent Account Balance: ${current_balance:.2f}"
            answer_output = run_agent(task_agent=task_agent, user_name="user", user_input=None, sys_message_suffix=suffix)
            if not answer_output:
                logging.warn("Agent returned no output...")
                num_errors += 1
                continue

            print(json.dumps(answer_output.get("output"), indent=2))
            num_errors = 0
        except Exception as e:
            traceback.print_exc()
            logging.error(f"Error: {e}")
            num_errors += 1
            if num_errors >= 3:
                logging.error(f"Max sequential errors reached, exiting...")
                break


if __name__ == "__main__":
    main()

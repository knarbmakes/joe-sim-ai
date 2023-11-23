import json
import os
import logging
from dotenv import load_dotenv
from src.core.file_based_context import FileBasedContext
from src.core.tool_agent import ObjectConfig, TextConfig, ToolAgent

# IMPORTANT: Import all tools so registry can be populated
import src.tools.calculator
import src.tools.host_action
import src.tools.host_plan
import src.tools.world_change
import src.tools.perception_update

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize Host Agent
fred_agent = ToolAgent(
    TextConfig(
        agent_key="fred",
        model="gpt-4-1106-preview",
        budget_dollars=5.0,
        available_functions=["calculate", "action", "plan"],
        system_message="\n".join(
            [
                "You act as the simulated brain functions of a human being, taking discrete actions based on your perceptions and internal thoughts.",
                "After processing the current perceptions and given working memory set, you make an brief internal plan first, and then proceed to act on it.",
                "All the plans/actions you make are queued up and executed in order. Once finished, reply with a simple 'done' message.",
                "Make sure to specify the concrete details about actions or thoughts, and avoid vague or abstract statements.",
                "Limit your action count to 2-3 per turn before sending the 'done' message.",
            ]
        ),
        kwargs={},
    ),
    ObjectConfig(
        agent_id=f"agent_fred", agent_service=FileBasedContext()
    ),
)

# Initialize the World Simulator Agent
world_simulator_agent = ToolAgent(
    TextConfig(
        agent_key="worldsim",
        model="gpt-4-1106-preview",
        budget_dollars=5.0,
        available_functions=["calculate", "world_change", "perception_update"],
        system_message="\n".join(
            [
                "You act as the simulated environment of the real world, providing changes based on a setting and list of events.",
                "You will quickly detail how the world/environment changes in response to a series of actions/events, and then proceed to update the perception object for each relevant actor.",
                "The perceptions you update should be specific and concrete, detailing proper nouns and vivid direct experiences."
                "Once you are done updating perceptions, reply with a simple 'done' message.",
            ]
        ),
        kwargs={},
    ),
    ObjectConfig(
        agent_id=f"agent_worldsim", agent_service=FileBasedContext()
    ),
)

# Starting scenario
world_simulator_input = [{"role": "user", "content": "Fred arrives at a busy cafe for dinner."}]

try:
    while True:
        # Step 1: World Simulator updates the environment and perceptions
        world_simulator_response = world_simulator_agent.run(world_simulator_input)
        logger.info(f"Response from World Simulator:\n{world_simulator_response}")

        # Read updated perceptions from file
        with open(f"tmp/{fred_agent.agent_key}_perceptions.json", "r") as file:
            updated_perceptions = json.load(file)
            logger.info(f"Updated perceptions: {updated_perceptions}")

        # Step 2: Run joe_agent with updated perceptions
        joe_response = fred_agent.run([{"role": "user", "content": "Process current perceptions and decide on appropriate actions. Perceptions: " + json.dumps(updated_perceptions)}])
        logger.info(f"Response from Host:\n{joe_response}")

        # Read actions from file
        with open(f"tmp/{fred_agent.agent_key}_actions.txt", "r") as file:
            actions_taken = file.readlines()

        # Clear the actions file after reading
        open(f"tmp/{fred_agent.agent_key}_actions.txt", "w").close()

        # Step 3: Feed actions back to the world simulator as input
        logger.info(f"Actions taken by Joe:\n{actions_taken}")
        world_simulator_input = [{"role": "user", "content": action} for action in actions_taken]

        # Wait for user input to continue or exit
        user_input = input("Press Enter to continue the simulation or type 'exit' to end: ")
        if user_input.lower() == 'exit':
            break

except Exception as e:
    logger.error(f"Error running ToolAgent: {e}")

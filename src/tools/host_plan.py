import json
import logging
from src.core.base_tool import BaseTool
from src.core.tool_registry import register_fn

# Configure logger for the Plan class
logger = logging.getLogger(__name__)

@register_fn
class Plan(BaseTool):
    @classmethod
    def get_name(cls) -> str:
        return "plan"
    
    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": "Represents the brief internal thoughts of a human based on a high-level plan.",
            "parameters": {
                "type": "object",
                "properties": {
                    "plan": {
                        "type": "string",
                        "description": "The near-term plan in a few brief sentences."
                    }
                },
                "required": ["plan"]
            }
        }
    
    @classmethod
    def run(cls, args: dict, agent_self: dict) -> str:
        validation_error = cls.validate_args(args, agent_self)
        if validation_error:
            return json.dumps({"error": f"Invalid arguments: {validation_error}"})
        
        plan = args['plan']

        internal_thought = f"{agent_self.agent_key} thinks, '{plan}'"

        # Log and append to file
        logger.info(internal_thought)
        with open(f"tmp/{agent_self.agent_key}_thoughts.txt", "a+") as file:
            file.write(internal_thought + "\n")

        return json.dumps({"result": "plan saved"})


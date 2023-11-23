import json
import logging
from src.core.base_tool import BaseTool
from src.core.tool_registry import register_fn

# Configure logger for the Action class
logger = logging.getLogger(__name__)

@register_fn
class Action(BaseTool):
    @classmethod
    def get_name(cls) -> str:
        return "action"
    
    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": "Queue an action or statement to make. For statements using type 'say', the details should be the verbatim text to say. For actions using type 'do', the details should be the action to perform.",
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "description": "Type of action, either 'say' or 'do'.",
                        "enum": ["say", "do"]
                    },
                    "details": {
                        "type": "string",
                        "description": "Details of the action to perform or say."
                    }
                },
                "required": ["type", "details"]
            }
        }
    
    @classmethod
    def run(cls, args: dict, agent_self: dict) -> str:
        validation_error = cls.validate_args(args, agent_self)
        if validation_error:
            return json.dumps({"error": f"Invalid arguments: {validation_error}"})
        
        action_type = args['type']
        details = args['details']

        action_verb = "says" if action_type == "say" else "does"

        action_sentence = f"{agent_self.agent_key} {action_verb} {details}"

        # Log and append to file
        logger.info(action_sentence)
        with open(f"tmp/{agent_self.agent_key}_actions.txt", "a+") as file:
            file.write(action_sentence + "\n")

        return json.dumps({"result": "queued"})

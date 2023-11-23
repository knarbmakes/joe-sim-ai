import json
import logging
from src.core.base_tool import BaseTool
from src.core.tool_registry import register_fn

# Configure logger for the WorldChange class
logger = logging.getLogger(__name__)

@register_fn
class WorldChange(BaseTool):
    @classmethod
    def get_name(cls) -> str:
        return "world_change"
    
    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": "Details how the world changes as a high-level plan. Should be called only once per turn.",
            "parameters": {
                "type": "object",
                "properties": {
                    "change": {
                        "type": "string",
                        "description": "Description of how the world changes."
                    }
                },
                "required": ["change"]
            }
        }
    
    @classmethod
    def run(cls, args: dict, agent_self: dict) -> str:
        validation_error = cls.validate_args(args, agent_self)
        if validation_error:
            return json.dumps({"error": f"Invalid arguments: {validation_error}"})
        
        change = args['change']

        world_change_statement = f"World Change: {change}"

        # Log and append to file
        logger.info(world_change_statement)
        with open(f"tmp/{agent_self.agent_key}_world_changes.txt", "a+") as file:
            file.write(world_change_statement + "\n")

        return json.dumps({"result": "world change processed"})


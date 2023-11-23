import json
import logging
import os
from src.core.base_tool import BaseTool
from src.core.tool_registry import register_fn

# Configure logger for the PerceptionUpdate class
logger = logging.getLogger(__name__)

@register_fn
class PerceptionUpdate(BaseTool):
    @classmethod
    def get_name(cls) -> str:
        return "perception_update"
    
    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": "Updates the subjective perception of the world for a specific actor. Represents how this person experiences the world.",
            "parameters": {
                "type": "object",
                "properties": {
                    "host_name": {
                        "type": "string",
                        "description": "The name of the host whose perception is being updated."
                    },
                    "perception": {
                        "type": "object",
                        "properties": {
                            "visual": {"type": "string"},
                            "auditory": {"type": "string"},
                            "olfactory": {"type": "string"},
                            "gustatory": {"type": "string"},
                            "proprioceptive": {"type": "string"},
                            "interoceptive": {"type": "string"}
                        },
                        "required": ["visual", "auditory", "olfactory", "gustatory", "proprioceptive", "interoceptive"],
                        "description": "Subjective sensory experiences of the host."
                    }
                },
                "required": ["host_name", "perception"]
            }
        }
    
    @classmethod
    def run(cls, args: dict, agent_self: dict) -> str:
        validation_error = cls.validate_args(args, agent_self)
        if validation_error:
            return json.dumps({"error": f"Invalid arguments: {validation_error}"})
        
        host_name = args['host_name'].lower()  # Convert host_name to lowercase
        perception = args['perception']

        perception_file_path = f"tmp/{host_name}_perceptions.json"  # The filename is now lowercase

        # Directly overwrite the file with new perception data
        with open(perception_file_path, 'w') as file:
            json.dump(perception, file, indent=2)

        logger.info(f"Perception updated for {host_name}")

        return json.dumps({"result": "perception updated"})

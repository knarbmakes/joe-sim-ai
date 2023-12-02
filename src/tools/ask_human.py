import json
import time
from core.base_tool import BaseTool
from core.tool_agent import ToolAgent
from core.tool_registry import register_fn

@register_fn
class AskHuman(BaseTool):

    @classmethod
    def get_name(cls) -> str:
        return "ask_human"
    
    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": "Ask a question to a human and get input. This is useful for getting your main goal or getting unblocked if you are stuck.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to be asked to the human"
                    }
                },
                "required": ["question"]
            }
        }

    @classmethod
    def run(cls, args: dict, agent_self: ToolAgent) -> str:
        validation_error = cls.validate_args(args, agent_self)
        if validation_error:
            return json.dumps({"error": f"Invalid arguments: {validation_error}"})

        question = args["question"]
        user_input = ''

        # Start the timer
        start_time = time.time()

        # Loop to ensure non-empty input
        while not user_input.strip():
            user_input = input(f"{question}\nEnter your response: ").strip()

            if not user_input:
                print("Input cannot be empty, please try again.")

        # Stop the timer
        end_time = time.time()
        response_latency = end_time - start_time

        return json.dumps({
            "response": user_input,
            "human_response_latency": response_latency
        })

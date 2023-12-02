import json
import logging
from core.base_tool import BaseTool
from core.tool_agent import ToolAgent
from core.tool_registry import register_fn
from asteval import Interpreter

@register_fn
class AstEval(BaseTool):
    @classmethod
    def get_name(cls) -> str:
        return "asteval"
    
    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": "Evaluate an expression using Python asteval.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Expression to evaluate."
                    }
                },
                "required": ["expression"]
            }
        }
    
    @classmethod
    def run(cls, args: dict, agent_self: ToolAgent) -> str:
        validation_error = cls.validate_args(args, agent_self)
        if validation_error:
            return json.dumps({"error": f"Invalid arguments: {validation_error}"})
        
        expression = args['expression']

        # Use asteval for safe evaluation
        safe_eval = Interpreter()
        try:
            result = safe_eval(expression)
        except Exception as e:
            return json.dumps({"error": str(e)})

        if result is None:
            return json.dumps({"error": "Invalid expression"})

        return json.dumps({"result": result})


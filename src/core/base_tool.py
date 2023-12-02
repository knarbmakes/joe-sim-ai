from jsonschema import ValidationError, validate
from core.tool_agent import ToolAgent

class BaseTool:
    @classmethod
    def get_name(cls) -> str:
        """Override this method to return the name of the function"""
        raise NotImplementedError("This method should be overridden by subclass")
    
    @classmethod
    def get_definition(cls, agent_self: ToolAgent) -> dict:
        """Override this method to return the JSON schema definition"""
        raise NotImplementedError("This method should be overridden by subclass")

    @classmethod
    def run(cls, args: dict, agent_self: ToolAgent) -> str:
        """Override this method to run the actual function"""
        raise NotImplementedError("This method should be overridden by subclass")

    @classmethod
    def validate_args(cls, args: dict, agent_self: ToolAgent) -> str:
        """Validate arguments based on the function's definition"""
        try:
            validate(instance=args, schema=cls.get_definition(agent_self)["parameters"])
            return ""
        except ValidationError as e:
            return str(e)

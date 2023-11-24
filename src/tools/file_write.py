import json
import os
import stat
from src.core.base_tool import BaseTool
from src.core.tool_registry import register_fn

@register_fn
class FileWrite(BaseTool):

    @classmethod
    def get_name(cls) -> str:
        return "file_write"
    
    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": "Writes contents to a specified file, creating the directory path if it does not exist, with optional chmod permissions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The path of the file to write to"
                    },
                    "contents": {
                        "type": "string",
                        "description": "The contents to write to the file"
                    },
                    "permissions": {
                        "type": "number",
                        "description": "The chmod permissions to set for the file (optional)"
                    }
                },
                "required": ["filepath", "contents"]
            }
        }

    @classmethod
    def run(cls, args: dict, agent_self: dict) -> str:
        validation_error = cls.validate_args(args, agent_self)
        if validation_error:
            return json.dumps({"error": f"Invalid arguments: {validation_error}"})

        filepath = args["filepath"]
        contents = args["contents"]
        permissions = args.get("permissions")

        # Ensure the directory for the file exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(contents)

            # Set file permissions if specified
            if permissions is not None:
                os.chmod(filepath, permissions)

            return json.dumps({"message": f"File written successfully at {filepath}"})

        except IOError as e:
            return json.dumps({"error": f"Error writing to file: {str(e)}"})
        except ValueError as e:
            return json.dumps({"error": f"Invalid permissions value: {str(e)}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {str(e)}"})

import json
from core.base_tool import BaseTool
from core.tool_agent import ToolAgent
from core.tool_registry import register_fn

MAX_FILE_SIZE = 5000  # Maximum characters to output

@register_fn
class FileRead(BaseTool):

    @classmethod
    def get_name(cls) -> str:
        return "file_read"
    
    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": "Reads contents from a file, providing details for continuation if the content is truncated due to size limits.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The filename of the file to read"
                    },
                    "cursor": {
                        "type": "number",
                        "description": "The cursor position to start reading from (optional)"
                    }
                },
                "required": ["filename"]
            }
        }

    @classmethod
    def run(cls, args: dict, agent_self: ToolAgent) -> str:
        validation_error = cls.validate_args(args, agent_self)
        if validation_error:
            return json.dumps({"error": f"Invalid arguments: {validation_error}"})

        filename = args["filename"]
        cursor = args.get("cursor", 0)

        try:
            with open(filename, 'r', encoding='utf-8') as file:
                file.seek(0,2)  # Move to the end of the file
                eof = file.tell()  # Get the position (char count)

                file.seek(cursor)  # Set cursor to the required position
                content = file.read(MAX_FILE_SIZE)

                final_cursor = file.tell()  # The new cursor position after reading
                truncated = final_cursor < eof  # Check if we reached the end of file

                # Construct the continuation hints
                continuation = {
                    "final_cursor": final_cursor,  # Updating to final_cursor
                    "eof": eof,
                    "truncated": truncated
                }

                return json.dumps({
                    "filename": filename,
                    "content": content,
                    "continuation": continuation
                })

        except FileNotFoundError:
            return json.dumps({"error": "File not found: {filename}"})
        except IOError as e:
            return json.dumps({"error": f"Error reading file: {str(e)}"})

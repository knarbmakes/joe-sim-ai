import json
from src.core.base_tool import BaseTool
from src.core.tool_registry import register_fn

MAX_FILE_SIZE = 5000

@register_fn
class FileRead(BaseTool):

    @classmethod
    def get_name(cls) -> str:
        return "file_read"
    
    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": f"Reads contents from a file. Reads at most {MAX_FILE_SIZE} characters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The filename of the file to read"
                    },
                    "line": {
                        "type": "number",
                        "description": "The line number to start reading from (optional)"
                    },
                    "column": {
                        "type": "number",
                        "description": "The column number to start reading from (optional)"
                    }
                },
                "required": ["filename"]
            }
        }

    @classmethod
    def run(cls, args: dict, agent_self: dict) -> str:
        validation_error = cls.validate_args(args, agent_self)
        if validation_error:
            return json.dumps({"error": f"Invalid arguments: {validation_error}"})

        filename = args["filename"]
        line_number = args.get("line")
        column_number = args.get("column")

        try:
            with open(filename, 'r', encoding='utf-8') as file:
                read_content = ''
                for current_line, content in enumerate(file, start=1):
                    if line_number is None or current_line >= line_number:
                        if current_line == line_number and column_number is not None:
                            content = content[column_number:]

                        read_content += content
                        if len(read_content) >= MAX_FILE_SIZE:
                            read_content = read_content[:MAX_FILE_SIZE]
                            break

                if line_number is not None and read_content == '':
                    return json.dumps({"error": "Specified line number not found"})

            return json.dumps({
                "filename": filename,
                "content": read_content
            })

        except FileNotFoundError:
            return json.dumps({"error": f"File not found: {filename}"})
        except IOError as e:
            return json.dumps({"error": f"Error reading file: {str(e)}"})


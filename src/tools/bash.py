import json
import subprocess
import time
from core.base_tool import BaseTool
from core.tool_registry import register_fn

@register_fn
class RunBashCommand(BaseTool):
    MAX_OUTPUT_LENGTH = 5000
    MAX_INPUT_LENGTH = 2000
    DEFAULT_COMMAND_TIMEOUT = 60  # Default timeout for command execution in seconds

    @classmethod
    def get_name(cls) -> str:
        return "bash"

    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": (f"Executes a specified bash command within a timeout and returns its output, "
                            f"limiting the output to the last {RunBashCommand.MAX_OUTPUT_LENGTH} characters. IMPORTANT: "
                            "Pay very close attention to escaping quotes and other special characters "
                            "when writing commands that write to files."),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": (f"The bash command to execute. Please ensure the command is concise, "
                                        f"as there is a maximum length of {RunBashCommand.MAX_INPUT_LENGTH} characters enforced "
                                        "for security and performance reasons.")
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Optional custom timeout in seconds for the command execution."
                    }
                },
                "required": ["command"]
            }
        }

    @classmethod
    def run(cls, args: dict, agent_self: dict) -> str:
        validation_error = cls.validate_args(args, agent_self)
        if validation_error:
            return json.dumps({"error": f"Invalid arguments: {validation_error}"})

        command = args["command"]
        custom_timeout = float(args.get("timeout", RunBashCommand.DEFAULT_COMMAND_TIMEOUT))

        if len(command) > RunBashCommand.MAX_INPUT_LENGTH:
            return json.dumps({"error": f"Command exceeds the maximum length of {RunBashCommand.MAX_INPUT_LENGTH} characters."})

        try:
            start_time = time.time()

            # Using subprocess.check_output
            output = subprocess.check_output(command, shell=True, text=True, timeout=custom_timeout)
            was_truncated = len(output) > RunBashCommand.MAX_OUTPUT_LENGTH
            output = output[-RunBashCommand.MAX_OUTPUT_LENGTH:]  # Truncate the output if it's too long

            end_time = time.time()
            duration = end_time - start_time

            result = {
                "status": 0,
                "output": output,
                "duration": f"{duration:.2f}s",
            }
            # if was_truncated, add the truncated key
            if was_truncated:
                result["truncated"] = f"NOTE: output was truncated to the last {RunBashCommand.MAX_OUTPUT_LENGTH} characters."
            return json.dumps(result)

        except subprocess.TimeoutExpired:
            return json.dumps({"error": f"Command timed out in {custom_timeout}s."})
        except subprocess.CalledProcessError as e:
            return json.dumps({"error": f"{e}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {str(e)}"})


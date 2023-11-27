import json
import subprocess
import time
from core.base_tool import BaseTool
from core.tool_registry import register_fn

MAX_OUTPUT_LENGTH = 5000  # Maximum characters to output
MAX_INPUT_LENGTH = 2000  # Maximum characters to input
COMMAND_TIMEOUT = 60     # Timeout for command execution in seconds

@register_fn
class RunBashCommand(BaseTool):

    @classmethod
    def get_name(cls) -> str:
        return "bash"
    
    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": f"Executes a specified bash command within a timeout and returns its output, limiting the output to the last {MAX_OUTPUT_LENGTH} characters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": f"The bash command to execute. Please ensure the command is concise, as there is a maximum length of {MAX_INPUT_LENGTH} characters enforced for security and performance reasons."
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
        if len(command) > MAX_INPUT_LENGTH:
            return json.dumps({"error": f"Command exceeds the maximum length of {MAX_INPUT_LENGTH} characters."})

        try:
            t0 = time.time()

            result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=COMMAND_TIMEOUT)
            stdout_tail = (result.stdout[-MAX_OUTPUT_LENGTH:] if len(result.stdout) > MAX_OUTPUT_LENGTH else result.stdout)
            stderr_tail = (result.stderr[-MAX_OUTPUT_LENGTH:] if len(result.stderr) > MAX_OUTPUT_LENGTH else result.stderr)

            tn = time.time()
            duration = tn - t0

            return json.dumps({
                "stdout": stdout_tail,
                "stderr": stderr_tail,
                "duration": f"{duration:.2f}s"
            })

        except subprocess.TimeoutExpired:
            return json.dumps({"error": "Command timed out in {COMMAND_TIMEOUT}s."})
        except subprocess.CalledProcessError as e:
            stderr_tail = e.stderr[-MAX_OUTPUT_LENGTH:] if len(e.stderr) > MAX_OUTPUT_LENGTH else e.stderr
            return json.dumps({"error": f"Command failed: {stderr_tail}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {str(e)}"})

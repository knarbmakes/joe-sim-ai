import json
import concurrent.futures
import logging
import traceback

from core.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class FunctionCallHandler:
    def __init__(self, agent_key, text_config, object_config):
        self.agent_key = agent_key
        self.text_config = text_config
        self.object_config = object_config

        self.agent_service = object_config.agent_service
        self.agent_id = object_config.agent_id
        function_names = text_config.available_functions or []
        self.available_functions = {
            name: ToolRegistry.functions[name]
            for name in function_names
            if name in ToolRegistry.functions
        }

    def get_available_fn_defn(self):
        # If the list is empty, return None to avoid an error
        result = [
            {"type": "function", "function": fn_cls.get_definition(self)}
            for fn_cls in self.available_functions.values()
        ]
        return result if result else None

    def update_context_with_response(self, tool_call, response, is_error=False):
        """
        Update the context memory with the response of a function call.
        """
        content = json.dumps({"error": response}) if is_error else response
        self.agent_service.update_context_memory(
            [
                {
                    "tool_call_id": tool_call["id"],
                    "role": "tool",
                    "name": tool_call["function"]["name"],
                    "content": content,
                }
            ],
        )

    def execute_function_call(self, tool_call):
        """
        Execute a single function call.
        """
        try:
            function_name = tool_call["function"]["name"]
            function_args = json.loads(tool_call["function"]["arguments"])
        except Exception as e:
            traceback.print_exc()
            logger.warn(
                f"execute_function_call failed to parse tool call {tool_call}. Error: {e}"
            )
            return json.dumps(
                {"error": f"Invalid function name or args structure. Error: {e}"}
            )

        if function_name not in self.available_functions:
            logger.warn(
                f"Function {function_name} not found in available functions: {self.available_functions}"
            )
            return json.dumps({"error": f"Function {function_name} not found!"})
        else:
            logger.info(f"Executing function {function_name} with args {function_args}")
            return self.available_functions[function_name].run(function_args, self)


    def handle_fn_calls(self, tool_calls):
        """
        Handle multiple function calls in parallel.
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_tool_call = {
                executor.submit(self.execute_function_call, tool_call): tool_call
                for tool_call in tool_calls
            }

            for future in concurrent.futures.as_completed(future_to_tool_call):
                tool_call = future_to_tool_call[future]
                try:
                    function_response = future.result()
                    self.update_context_with_response(tool_call, function_response)
                except Exception as exc:
                    traceback.print_exc()
                    logger.warn(
                        f"Function call {tool_call} generated an exception: {exc}"
                    )
                    self.update_context_with_response(
                        tool_call, str(exc), is_error=True
                    )
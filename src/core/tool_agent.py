import json
import openai
import os
import traceback
import logging

from dotenv import load_dotenv
from src.core.cost_helper import calculate_cost, get_context_window, num_tokens_from_message, num_tokens_from_string
from src.core.tool_registry import ToolRegistry
from typing import NamedTuple, Dict, Any, Optional
import concurrent.futures

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
openai_client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

class TextConfig(NamedTuple):
    agent_key: Optional[str]
    model: str
    budget_dollars: float
    available_functions: list[str]
    system_message: Optional[str]
    kwargs: Dict[str, Any]

class ObjectConfig(NamedTuple):
    agent_id: str
    agent_service: Any


class ToolAgent:
    def __init__(self, text_config: TextConfig, object_config: ObjectConfig):
        # Every agent needs a key, so generate one if it is not provided.
        self.agent_key = text_config.agent_key or os.urandom(16).hex()

        # text_config contains llm or user defined parameters
        self.text_config = text_config

        # budget tracking
        self.total_cost = 0

        # object_config contains system level configuration objects and variables.
        # things that only our code needs to know about.
        self.object_config = object_config
        self.agent_service = object_config.agent_service

        # Turn text_config.available_functions into a dictionary of actual function objects
        function_names = text_config.available_functions or []
        self.available_functions = {name: ToolRegistry.functions[name] for name in function_names if name in ToolRegistry.functions}

    def can_run(self):
        return True

    def track_usage(self, usage):
        # Update budget in the object and in the database
        cost = calculate_cost(dict(usage), self.text_config.model)
        self.total_cost += cost
        logger.info(f'Usage to budget: COST = {cost} dollars for agent {self.agent_key}')

    def get_available_fn_defn(self):
        # If the list is empty, return None to avoid an error
        result = [{ "type": "function", "function": fn_cls.get_definition(self)} for fn_cls in self.available_functions.values()]
        return result if result else None

    def build_message_stack(self):
        system_message = self.text_config.system_message or 'You are a helpful assistant.'

        # Figure out what our message token cap is. This involves getting the model context window and subtracting the system message tokens and some buffer for the response.
        model_context_window = get_context_window(self.text_config.model)
        response_generation_tokens = 500 # This is some sane default to allow us to generate at least some response.
        max_limit = model_context_window - num_tokens_from_string(system_message, self.text_config.model) - response_generation_tokens

        # Get the latest context memory.
        chat_history = self.agent_service.update_context_memory(self.object_config.agent_id, memory_elements=[]) or []

        # Pre-calculate the token counts for all messages in chat history.
        token_counts = [num_tokens_from_message(m, self.text_config.model) for m in chat_history]
        
        # Make sure we don't exceed the token cap, popping messages from the chat history if we do.
        total_tokens = sum(token_counts)
        final_count = len(chat_history)
        
        while total_tokens > max_limit:
            # Reduce the total_tokens by the tokens from the oldest message that we are about to remove.
            total_tokens -= token_counts.pop(0)
            
            # Pop the oldest message from the chat history.
            chat_history.pop(0)
            final_count -= 1

        # Pop the messages from the database as well so we don't keep growing the list infinitely.
        if final_count < len(chat_history):
            self.agent_service.update_context_memory(self.object_config.agent_id, memory_elements=None, final_count=final_count)

        # Iterate over all messages, and flip assistant to u ser if it is not us.
        for msg in chat_history:
            if msg['role'] == 'assistant' and msg.get('name') and msg['name'] != self.agent_key:
                msg['role'] = 'user'

        # Build the message stack
        messages = [{"role": "system", "content": system_message}, *chat_history]
        logger.debug(f"Final message stack for {self.agent_key}: {json.dumps(messages, indent=2)}")
        return messages

    def handle_fn_call(self, tool_calls):
        """
        Handle multiple function calls in parallel.
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit all function calls to the executor
            future_to_tool_call = {executor.submit(self._execute_function_call, tool_call): tool_call for tool_call in tool_calls}

            for future in concurrent.futures.as_completed(future_to_tool_call):
                tool_call = future_to_tool_call[future]
                try:
                    function_response = future.result()
                except Exception as exc:
                    traceback.print_exc()  # Print the stack trace
                    logger.warn(f'Function call {tool_call} generated an exception: {exc}')
                    self.agent_service.update_context_memory(self.object_config.agent_id, [{
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": tool_call["function"]["name"],
                        "content": {"error": f"{exc}"}
                    }])
                else:
                    # Append the response with the required structure
                    self.agent_service.update_context_memory(self.object_config.agent_id, [{
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": tool_call["function"]["name"],
                        "content": function_response
                    }])

    def _execute_function_call(self, tool_call):
        """
        Execute a single function call.
        """
        try:
            function_name = tool_call["function"]["name"]
            function_args = json.loads(tool_call["function"]["arguments"])
        except Exception as e:
            return {"error": f"Invalid function call structure. Error: {e}"}

        # Execute the function and get the response
        if function_name not in self.available_functions:
            return {"error": f"Function {function_name} not found!"}
        else:
            return self.available_functions[function_name].run(function_args, self)


    def run(self, input_messages=None, system_message_override=None):
        try:
            if not self.can_run():
                return None
            
            budget_dollars = self.text_config.budget_dollars or 5.0

            # Update context memory with input messages if any, before starting the loop
            if input_messages:
                self.agent_service.update_context_memory(self.object_config.agent_id, memory_elements=input_messages)

            # Update system message if it's overridden
            if system_message_override:
                self.text_config.system_message = system_message_override

            # Loop until we stop getting function calls or we exceed the budget.
            while True:
                if self.total_cost > budget_dollars:
                    logger.warning(f'Budget exceeded for agent {self.agent_key}. Stopping execution.')
                    return {"error": "Budget limit exceeded"}
                
                messages = self.build_message_stack()
                kwargs = self.text_config.kwargs or {}

                # Add functions to the kwargs if they are available
                available_function_definitions = self.get_available_fn_defn()
                if available_function_definitions:
                    kwargs['tools'] = available_function_definitions

                completion = openai_client.chat.completions.create(
                    model=self.text_config.model,
                    messages=messages,
                    timeout=90,
                    **kwargs
                )

                # Log budget based on usage
                self.track_usage(dict(completion).get('usage'))

                # Handle explicit function calls
                output = dict(completion.choices[0].message)
                if "tool_calls" in output and output["tool_calls"] is not None:
                    # Convert tool_calls to serializable format
                    tool_calls_serializable = [tool_call.dict() for tool_call in output["tool_calls"]]

                    # Update context memory with serializable tool calls
                    self.agent_service.update_context_memory(self.object_config.agent_id, [{"role": "assistant", "content": output.get("content"), "tool_calls": tool_calls_serializable}])

                    # Process the tool calls
                    self.handle_fn_call(tool_calls_serializable)
                else:
                    # Save the output to context memory and return.
                    self.agent_service.update_context_memory(self.object_config.agent_id, [{"role": "assistant", "content": output.get("content")}])
                    logger.info(f"Agent {self.agent_key} final output: {output}")
                    return output
        except Exception as e:
            traceback.print_exc()  # Print the stack trace
            logger.exception(f'An error occurred in agent {self.agent_key}: {e}')
            return {"error": f"An error occurred: {e}"}


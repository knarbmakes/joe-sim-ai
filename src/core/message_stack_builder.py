import json
import logging
from core.cost_helper import get_context_window, num_tokens_from_message, num_tokens_from_string

logger = logging.getLogger(__name__)

class MessageStackBuilder:
    def __init__(self, agent_key, text_config, object_config):
        self.agent_service = object_config.agent_service
        self.agent_id = object_config.agent_id
        self.agent_key = agent_key
        self.text_config = text_config

    def build_message_stack(self, sys_message_suffix=None):
        system_message = (
            (self.text_config.system_message or "You are a helpful assistant.") + (f" {sys_message_suffix}" if sys_message_suffix else "")
        )

        # Figure out what our message token cap is. This involves getting the model context window and subtracting the system message tokens and some buffer for the response.
        model_context_window = get_context_window(self.text_config.model)
        response_generation_tokens = 500  # This is some sane default to allow us to generate at least some response.
        max_limit = (
            model_context_window
            - num_tokens_from_string(system_message, self.text_config.model)
            - response_generation_tokens
        )

        # Get the latest context memory.
        chat_history = (
            self.agent_service.update_context_memory(memory_elements=[])
            or []
        )

        # Pre-calculate the token counts for all messages in chat history.
        token_counts = [
            num_tokens_from_message(m, self.text_config.model) for m in chat_history
        ]

        # Make sure we don't exceed the token cap, popping messages from the chat history if we do.
        total_tokens = sum(token_counts)
        final_count = len(chat_history)

        while total_tokens > max_limit:
            # Reduce the total_tokens by the tokens from the oldest message that we are about to remove.
            total_tokens -= token_counts.pop(0)

            # Pop the oldest message from the chat history.
            chat_history.pop(0)
            final_count -= 1

        # After trimming the list for token limits, remove any messages with role = tool from the start of the list
        while chat_history and chat_history[0]["role"] == "tool":
            chat_history.pop(0)
            final_count -= 1

        # Pop the messages from the database as well so we don't keep growing the list infinitely.
        if final_count < len(chat_history):
            self.agent_service.update_context_memory(
                memory_elements=None,
                final_count=final_count,
            )

        # Iterate over all messages, and flip assistant to u ser if it is not us.
        for msg in chat_history:
            if (
                msg["role"] == "assistant"
                and msg.get("name")
                and msg["name"] != self.agent_key
            ):
                msg["role"] = "user"

        # Build the message stack
        messages = [{"role": "system", "content": system_message}, *chat_history]
        logger.debug(
            f"Final message stack for {self.agent_key}: {json.dumps(messages, indent=2)}"
        )
        return messages
import json
import os
from typing import List, Dict


class FileBasedContext:
    def __init__(self, agent_id: str, folder: str):
        self.folder = folder
        self.agent_id = agent_id

    def update_context_memory(self, memory_elements: List[Dict] = [], final_count: int = 0) -> List[Dict]:
        file_path = f"{self.folder}/{self.agent_id}_context_memory.json"
        context_memory = []

        # Ensure the tmp directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Read existing context memory
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                context_memory = json.load(file)

        # Update context memory if we have new memory elements
        if len(memory_elements) > 0:
            context_memory.extend(memory_elements)

        # Slice context memory if final_count is provided, we want to keep the most recent messages
        if final_count > 0:
            context_memory = context_memory[-final_count:]

        # Write updated context memory back to file
        with open(file_path, "w") as file:
            json.dump(context_memory, file, indent=2)

        return context_memory

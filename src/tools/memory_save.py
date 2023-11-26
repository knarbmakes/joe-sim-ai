
import json
import logging
import traceback
import chromadb
from ulid import ULID
from core.base_tool import BaseTool
from core.tool_registry import register_fn
from datetime import datetime

# Configure logger for the ChromaDBSave class
logger = logging.getLogger(__name__)

@register_fn
class MemorySave(BaseTool):
    @classmethod
    def get_name(cls) -> str:
        return "memory_save"

    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": "Save a memory document to ChromaDB. Useful if you have something you want to remember for a long time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "truth_score": {
                        "type": "number",
                        "description": "Numerical confidence score from 1-100 on this memory. Higher numbers mean you are convinced this is a truthful memory."
                    },
                    "label": {
                        "type": "string",
                        "description": "Short string identifier to label the memory as a title."
                    },
                    "details": {
                        "type": "string",
                        "description": "The meat of the memory, capturing the most important things to remember for the future."
                    },
                    "type": {
                        "type": "string",
                        "description": "The type of memory, e.g., 'fact', 'idea', 'plan', 'goal', 'insight', 'question', 'answer', 'task', 'reminder', 'note', 'thought', 'feeling', 'event', 'experience', 'story', 'quote', 'image', 'video', 'audio', 'link', 'file', 'other'."
                    },
                },
                "required": ["truth_score", "label", "details", "type"]
            }
        }
    
    @classmethod
    def run(cls, args: dict, agent_self: dict) -> str:
        validation_error = cls.validate_args(args, agent_self)
        if validation_error:
            return json.dumps({"error": f"Invalid arguments: {validation_error}"})
        
        memory_id = str(ULID())
        document = str(args['details'])
        metadata = {
            "id": memory_id,
            "truth_score": str(args['truth_score']),
            "label": str(args['label']),
            "type": str(args['type']),
            "created_at": str(datetime.utcnow().isoformat())
        }
        collection = agent_self.object_config.chroma_db_collection
        
        try:
            collection.add(documents=[document], metadatas=[metadata], ids=[memory_id])
        except Exception as e:
            traceback.print_exc()  # Print the stack trace
            logger.error(f"Error in saving memory: {e}")
            return json.dumps({"error": str(e)})

        logger.info(f"Memory saved successfully with ID: {memory_id}")
        return json.dumps({"result": "Memory saved successfully", "memory_id": memory_id})


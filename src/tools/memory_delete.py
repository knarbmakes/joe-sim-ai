import json
import logging
import traceback
import chromadb
from core.base_tool import BaseTool
from core.tool_registry import register_fn

# Configure logger for the MemoryDelete class
logger = logging.getLogger(__name__)

@register_fn
class MemoryDelete(BaseTool):
    @classmethod
    def get_name(cls) -> str:
        return "memory_delete"

    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": "Delete memories from ChromaDB either by a list of IDs or using a where filter.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of memory IDs to delete."
                    },
                    "where": {
                        "type": "string",
                        "description": "Optional JSON string for filtering which memories to delete. Example: '{\"type\": \"fact\"}'"
                    }
                },
                "additionalProperties": False
            }
        }

    @classmethod
    def run(cls, args: dict, agent_self: dict) -> str:
        validation_error = cls.validate_args(args, agent_self)
        if validation_error:
            return json.dumps({"error": f"Invalid arguments: {validation_error}"})

        ids = args.get('ids', [])
        where_clause = json.loads(args['where']) if 'where' in args else None
        collection = agent_self.object_config.chroma_db_collection

        try:
            collection.delete(ids=ids, where=where_clause)
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error in deleting memories: {e}")
            return json.dumps({"error": str(e)})

        logger.info("Memories deleted successfully.")
        return json.dumps({"result": "Memories deleted successfully"})

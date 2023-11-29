import json
import logging
import traceback
from core.base_tool import BaseTool
from core.idgen import generate_id
from core.tool_registry import register_fn
from datetime import datetime

logger = logging.getLogger(__name__)

@register_fn
class MemoryUpsert(BaseTool):
    @classmethod
    def get_name(cls) -> str:
        return "memory_upsert"

    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": "Upsert a memory document to ChromaDB. Can be used to create or update a memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Optional unique identifier for the memory. If provided, updates an existing memory."
                    },
                    "label": {
                        "type": "string",
                        "description": "Short string identifier to label the memory as a title."
                    },
                    "details": {
                        "type": "string",
                        "description": "Details of the memory."
                    },
                    "type": {
                        "type": "string",
                        "description": "The type of memory."
                    },
                },
                "required": []
            }
        }

    @classmethod
    def run(cls, args: dict, agent_self: dict) -> str:
        if "id" not in args:
            required_fields = ["label", "details", "type"]
            for field in required_fields:
                if field not in args:
                    return json.dumps({"error": f"Missing required field: {field}"})

            args["id"] = generate_id(6)  # Generate a new ID if not provided

        document = str(args.get('details', ''))
        metadata = {
            "id": args["id"],
            "label": str(args.get('label', '')),
            "type": str(args.get('type', ''))
        }
        if "id" not in args:
            metadata["created_at"] = str(datetime.utcnow().isoformat())
        collection = agent_self.object_config.chroma_db_collection

        try:
            # Use upsert method to insert or update the document based on the provided ID
            collection.upsert(documents=[document], metadatas=[metadata], ids=[args["id"]])
        except Exception as e:
            traceback.print_exc()  # Print the stack trace
            logger.error(f"Error in upserting memory: {e}")
            return json.dumps({"error": str(e)})

        logger.info(f"Memory upserted successfully with ID: {args['id']}")
        return json.dumps({"result": "Memory upserted successfully", "memory_id": args['id']})

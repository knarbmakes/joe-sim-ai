import json
import logging
import traceback
import chromadb
from core.base_tool import BaseTool
from core.tool_registry import register_fn

# Configure logger for the QueryMemories class
logger = logging.getLogger(__name__)

@register_fn
class MemoryQuery(BaseTool):
    @classmethod
    def get_name(cls) -> str:
        return "memory_query"

    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": "Query memories from ChromaDB based on a text query. You should be calling this a lot to get long-term memories out of ChromaDB while helping the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query_text": {
                        "type": "string",
                        "description": "The text to query against the memories."
                    },
                    "n_results": {
                        "type": "number",
                        "description": "The number of query results to return."
                    },
                    "where": {
                        "type": "string",
                        "description": "Optional JSON string for filtering based on metadata fields. Example: '{\"type\": \"fact\"}'"
                    },
                    "where_document": {
                        "type": "string",
                        "description": "Optional JSON string for filtering based on document content. Example: '{\"$contains\":\"search_string\"}'"
                    }
                },
                "required": ["query_text", "n_results"]
            }
        }

    @classmethod
    def run(cls, args: dict, agent_self: dict) -> str:
        validation_error = cls.validate_args(args, agent_self)
        if validation_error:
            return json.dumps({"error": f"Invalid arguments: {validation_error}"})

        try:
            query_text = args['query_text']
            n_results = args['n_results']
            where_clause = json.loads(args['where']) if 'where' in args else None
            where_document_clause = json.loads(args['where_document']) if 'where_document' in args else None
            collection = agent_self.object_config.chroma_db_collection
            raw_results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where_clause,
                where_document=where_document_clause
            )
            # Transform raw results into a more readable format
            memory_objects = cls._format_results(raw_results)
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error in querying memories: {e}")
            return json.dumps({"error": str(e)})

        logger.info("Query executed successfully.")
        return json.dumps({"result": memory_objects})

    @classmethod
    def _format_results(cls, raw_results):
        formatted_results = []
        for ids, distances, metadatas, documents in zip(
            raw_results['ids'], raw_results['distances'], raw_results['metadatas'], raw_results['documents']
        ):
            for id, distance, metadata, document in zip(ids, distances, metadatas, documents):
                memory = {
                    "id": id,
                    "distance": distance,
                    "metadata": metadata,
                    "document": document
                }
                formatted_results.append(memory)
        return formatted_results

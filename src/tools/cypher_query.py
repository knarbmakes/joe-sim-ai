import json
import logging
import traceback
from core.base_tool import BaseTool
from core.tool_agent import ToolAgent
from core.tool_registry import register_fn

# Configure logger for the CypherQuery class
logger = logging.getLogger(__name__)

@register_fn
class CypherQuery(BaseTool):
    @classmethod
    def get_name(cls) -> str:
        return "cypher_query"

    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": "Execute a Cypher query on the Neo4j database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The Cypher query to execute. Example usage: 'CREATE (a:Person {name: $name, age: $age})'."
                    },
                    "parameters": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": "Optional. A dictionary of parameters for the Cypher query. This dictionary allows for the dynamic passing of values to the Cypher query. For instance, if your query includes variables like $name and $age, you can pass these values in the parameters dictionary. Example usage: For a query 'CREATE (a:Person {name: $name, age: $age})', you can pass parameters as {'name': 'Alice', 'age': 30}. This approach helps prevent Cypher Injection vulnerabilities and ensures that variable content is correctly formatted and escaped."
                    }
                },
                "required": ["query"]
            }
        }

    @classmethod
    def run(cls, args: dict, agent_self: ToolAgent) -> str:
        try:
            query = args['query']
            parameters = args.get('parameters', {})

            if parameters and not isinstance(parameters, dict):
                raise ValueError("The 'parameters' must be a dictionary.")

            result = agent_self.object_config.neo4j.execute_query(query, parameters)
        except ValueError as ve:
            return json.dumps({"error": str(ve)})
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error in executing Cypher query: {e}")
            return json.dumps({"error": str(e)})

        return json.dumps({"result": result})

import json
import os
import requests
from dotenv import load_dotenv
from core.base_tool import BaseTool
from core.tool_agent import ToolAgent
from core.tool_registry import register_fn

@register_fn
class WebSearch(BaseTool):

    @classmethod
    def get_name(cls) -> str:
        return "web_search"
    
    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": "Search the web using the Serper API",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "num": {
                        "type": "number",
                        "description": "Number of search results to return"
                    }
                },
                "required": ["query"]
            }
        }

    @classmethod
    def run(cls, args: dict, agent_self: ToolAgent) -> str:
        validation_error = cls.validate_args(args, agent_self)
        if validation_error:
            return json.dumps({"error": f"Invalid arguments: {validation_error}"})

        # Load environment variables
        load_dotenv()

        # Retrieve the Serper API key from environment variables
        SERPER_API = os.getenv("SERPER_API")

        # Prepare API request
        url = "https://google.serper.dev/search"
        payload = json.dumps({
            "q": args["query"],
            "gl": "us",
            "hl": "en",
            "num": args.get("num", 5),  # Default to 4 if num is not provided
            "page": 1,
            "type": "search",
            "engine": "google"
        })
        headers = {
          'X-API-KEY': SERPER_API,
          'Content-Type': 'application/json'
        }

        # Make API call
        response = requests.request("POST", url, headers=headers, data=payload)
        response_data = json.loads(response.text)

        # Extract knowledgeGraph and top organic results
        knowledge_graph = response_data.get('knowledgeGraph', {})
        top_results = response_data.get('organic', [])

        return json.dumps({
            "knowledge_graph": knowledge_graph,
            "top_results": top_results
        })

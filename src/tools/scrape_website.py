import json
import requests
from bs4 import BeautifulSoup
from src.core.base_tool import BaseTool
from src.core.tool_registry import register_fn
from urllib.parse import urlparse
from datetime import datetime
import os

@register_fn
class ScrapeWebsite(BaseTool):

    @classmethod
    def get_name(cls) -> str:
        return "scrape_website"
    
    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": "Scrape a single page's HTML content and save it to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the page to scrape"
                    }
                },
                "required": ["url"]
            }
        }

    @classmethod
    def run(cls, args: dict, agent_self: dict) -> str:
        validation_error = cls.validate_args(args, agent_self)
        if validation_error:
            return json.dumps({"error": f"Invalid arguments: {validation_error}"})

        # Fetch the webpage
        response = requests.get(args["url"])
        if response.status_code != 200:
            return json.dumps({"error": f"Failed to fetch the page, status code: {response.status_code}"})

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')
        parsed_html = soup.prettify()

        # Generate a filename based on the URL's hostname and a timestamp
        hostname = urlparse(args["url"]).hostname
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"tmp/{hostname}_{timestamp}.html"

        # Save the parsed HTML to a file
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(parsed_html)

        return json.dumps({
            "url": args["url"],
            "filename": filename
        })

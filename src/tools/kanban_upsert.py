import json
import logging
import traceback
from core.base_tool import BaseTool
from core.tool_registry import register_fn
from core.file_based_kanban import Stage

# Configure logger for the KanbanUpsert class
logger = logging.getLogger(__name__)

@register_fn
class KanbanUpsert(BaseTool):
    @classmethod
    def get_name(cls) -> str:
        return "kanban_upsert"

    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": "Upsert a card on the Kanban board. Use this to add a new card or update an existing one.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "The ID of the card. If not provided, a new card will be created."
                    },
                    "name": {
                        "type": "string",
                        "description": "The name of the card. Required if creating a new card."
                    },
                    "description": {
                        "type": "string",
                        "description": "The description of the card. Should detail the task to be done."
                    },
                    "stage": {
                        "type": "string",
                        "enum": Stage.get_values(),
                        "description": "The stage of the card."
                    }
                },
                "required": []
            }
        }

    @classmethod
    def run(cls, args: dict, agent_self: dict) -> str:
        validation_error = cls.validate_args(args, agent_self)
        if validation_error:
            return json.dumps({"error": f"Invalid arguments: {validation_error}"})

        try:
            id = args.get('id', None)
            name = args['name']
            description = args['description']
            stage = Stage(args['stage'])
            kanban_board = agent_self.object_config.kanban_board
            kanban_board.upsert_card(name, description, stage, id)
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error in upserting Kanban card: {e}")
            return json.dumps({"error": str(e)})

        logger.info("Card upserted successfully.")
        return json.dumps({"result": "Card upserted successfully."})

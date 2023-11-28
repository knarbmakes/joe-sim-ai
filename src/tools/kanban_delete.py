import json
import logging
import traceback
from core.base_tool import BaseTool
from core.tool_registry import register_fn

# Configure logger for the KanbanDelete class
logger = logging.getLogger(__name__)

@register_fn
class KanbanDelete(BaseTool):
    @classmethod
    def get_name(cls) -> str:
        return "kanban_delete"

    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        return {
            "name": cls.get_name(),
            "description": "Delete a card from the Kanban board based on its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "card_id": {
                        "type": "string",
                        "description": "The ID of the card to be deleted."
                    }
                },
                "required": ["card_id"]
            }
        }

    @classmethod
    def run(cls, args: dict, agent_self: dict) -> str:
        card_id = args.get('card_id')
        if not card_id:
            return json.dumps({"error": "Card ID is required for deletion."})

        try:
            kanban_board = agent_self.object_config.kanban_board
            kanban_board.delete_card(card_id)
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error in deleting Kanban card: {e}")
            return json.dumps({"error": str(e)})

        logger.info("Card deleted successfully.")
        return json.dumps({"result": f"Card with ID {card_id} deleted successfully."})

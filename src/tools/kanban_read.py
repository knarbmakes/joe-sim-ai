import json
import logging
import traceback
from core.base_tool import BaseTool
from core.tool_agent import ToolAgent
from core.tool_registry import register_fn
from core.file_based_kanban import Stage

# Configure logger for the KanbanRead class
logger = logging.getLogger(__name__)

@register_fn
class KanbanRead(BaseTool):
    @classmethod
    def get_name(cls) -> str:
        return "kanban_read"

    @classmethod
    def get_definition(cls, agent_self: dict) -> dict:
        stage_values = [stage.value for stage in Stage]
        return {
            "name": cls.get_name(),
            "description": "Read cards from the Kanban board. You can filter by stage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "stage": {
                        "type": "string",
                        "enum": stage_values,
                        "description": "Optional. The stage to filter the cards by."
                    }
                },
                "required": []
            }
        }

    @classmethod
    def run(cls, args: dict, agent_self: ToolAgent) -> str:
        try:
            stage = args.get('stage')
            if stage is not None:
                stage = Stage(stage)
            kanban_board = agent_self.object_config.kanban_board
            cards = kanban_board.read_board(stage)
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error in reading Kanban board: {e}")
            return json.dumps({"error": str(e)})

        logger.info("Board read successfully.")
        return json.dumps({"result": cards})


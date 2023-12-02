from core.file_based_bank_account import FileBasedBankAccount
from core.file_based_context import FileBasedContext
from core.file_based_kanban import FileBasedKanbanBoard
from typing import NamedTuple, Optional, Dict, Any


class TextConfig(NamedTuple):
    agent_key: Optional[str]
    model: str
    available_functions: list[str]
    system_message: Optional[str]
    kwargs: Dict[str, Any]


class ObjectConfig(NamedTuple):
    agent_id: str
    agent_service: FileBasedContext
    bank_account: FileBasedBankAccount
    chroma_db_collection: Any
    kanban_board: FileBasedKanbanBoard
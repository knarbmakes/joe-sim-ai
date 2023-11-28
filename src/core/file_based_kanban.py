import json
import os
import threading
from datetime import datetime
from enum import Enum
from ulid import ULID

class Stage(Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class FileBasedKanbanBoard:
    _lock = threading.Lock()

    def __init__(self, board_id: str, folder: str):
        self.board_id = board_id
        self.file_path = f"{folder}/{board_id}_kanban_board.json"
        self._ensure_board_file()

    def _ensure_board_file(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as file:
                json.dump([], file, indent=2)

    @staticmethod
    def _read_board_data(file_path: str) -> list:
        with open(file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def _write_board_data(file_path: str, data: list):
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)

    def read_board(self, stage=None) -> list:
        with FileBasedKanbanBoard._lock:
            cards = self._read_board_data(self.file_path)
            active_cards = [card for card in cards if not card.get('archived', False)]
            if stage:
                return [card for card in active_cards if card['stage'] == stage.value]
            return active_cards

    def upsert_card(self, name=None, description=None, stage=None, card_id=None) -> str:
        with FileBasedKanbanBoard._lock:
            cards = self._read_board_data(self.file_path)
            if card_id:
                # Update existing card
                for card in cards:
                    if card['id'] == card_id:
                        if name is not None:
                            card['name'] = name
                        if description is not None:
                            card['description'] = description
                        if stage is not None:
                            card['stage'] = stage.value
                        card['updated'] = datetime.now().isoformat()
                        self._write_board_data(self.file_path, cards)
                        return card_id

            # Create new card if no ID is provided or ID not found
            new_id = str(ULID())
            new_card = {
                'id': new_id,
                'name': name,
                'description': description,
                'stage': stage.value if stage else None,
                'created': datetime.now().isoformat(),
                'updated': datetime.now().isoformat()
            }
            cards.append(new_card)
            self._write_board_data(self.file_path, cards)
            return new_id

    def delete_card(self, card_id: str):
        with FileBasedKanbanBoard._lock:
            cards = self._read_board_data(self.file_path)
            for card in cards:
                if card['id'] == card_id:
                    card['archived'] = True
                    card['updated'] = datetime.now().isoformat()
                    break
            self._write_board_data(self.file_path, cards)

# Example usage:
# kanban = FileBasedKanbanBoard("my_kanban", "/path/to/folder")
# kanban.upsert_card(name="Task 1", description="Description of Task 1", stage=Stage.TODO)
# => returns "123"
# kanban.upsert_card(name="Task 1 modified", stage=Stage.IN_PROGRESS, card_id="123")
# print(kanban.read_board())
# print(kanban.read_board(Stage.TODO))
# kanban.delete_card("123")

from decimal import Decimal
import json
import os
import threading
from datetime import datetime

class FileBasedBankAccount:
    _lock = threading.Lock()

    def __init__(self, account_id: str, folder: str):
        self.account_id = account_id
        self.file_path = f"{folder}/{account_id}_bank_account.json"
        self.transaction_log_path = f"{folder}/{account_id}_transactions.log"
        self._ensure_account_file()
        self._ensure_transaction_log_file()

    def _ensure_transaction_log_file(self):
        # Ensure the transaction log file exists
        os.makedirs(os.path.dirname(self.transaction_log_path), exist_ok=True)
        if not os.path.exists(self.transaction_log_path):
            with open(self.transaction_log_path, 'w') as file:
                file.write("")

    def _log_transaction(self, transaction: dict):
        # Convert Decimal to str for JSON serialization
        transaction = {k: str(v) if isinstance(v, Decimal) else v for k, v in transaction.items()}
        with open(self.transaction_log_path, 'a') as file:
            file.write(json.dumps(transaction) + "\n")

    def _ensure_account_file(self):
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w') as file:
                json.dump({"balance": 100}, file, indent=2)

    @staticmethod
    def _read_account_data(file_path: str) -> dict:
        with open(file_path, 'r') as file:
            data = json.load(file)
            # Convert str to Decimal
            data["balance"] = Decimal(data["balance"])
            return data

    @staticmethod
    def _write_account_data(file_path: str, data: dict):
        data = {k: str(v) if isinstance(v, Decimal) else v for k, v in data.items()}
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)

    def get_balance(self) -> Decimal:
        with FileBasedBankAccount._lock:
            account_data = self._read_account_data(self.file_path)
            return account_data["balance"]

    def subtract_balance(self, amount: Decimal, agent_id: str) -> bool:
        with FileBasedBankAccount._lock:
            account_data = self._read_account_data(self.file_path)

            # Allow going into overdraft but block spending if already in overdraft
            if account_data["balance"] < 0:
                return False  # Already in overdraft, block further spending

            account_data["balance"] -= amount
            transaction = {
                "agent_id": agent_id, 
                "amount": amount, 
                "overdraft": account_data["balance"] < 0,
                "timestamp": datetime.now().isoformat()
            }

            # Log the transaction
            self._log_transaction(transaction)
            self._write_account_data(self.file_path, account_data)

            return True

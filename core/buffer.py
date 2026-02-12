import csv
from config import RAW_DATA_FILE

class Buffer:
    def __init__(self):
        self.stack = []

    def add(self, record):
        self.stack.append(record)

    def flush(self):
        if not self.stack:
            return
        file_exists = False
        try:
            with open(RAW_DATA_FILE, "r", encoding="utf-8"):
                file_exists = True
        except FileNotFoundError:
            file_exists = False
        with open(RAW_DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.stack[0].keys())
            if not file_exists:
                writer.writeheader()
            for r in self.stack:
                writer.writerow(r)
        self.stack.clear()

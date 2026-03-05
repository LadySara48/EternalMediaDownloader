"""
✨ Eternal Media Downloader | Developed by Hearlov — History Manager
Persistent download history stored in data/history.json
"""

import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional


HISTORY_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
HISTORY_FILE = os.path.join(HISTORY_DIR, "history.json")


@dataclass
class HistoryEntry:
    title: str
    url: str
    format_type: str
    quality: str
    file_path: str
    status: str
    date: str = ""
    uploader: str = ""

    def __post_init__(self):
        if not self.date:
            self.date = datetime.now().strftime("%Y-%m-%d %H:%M")


class HistoryManager:
    _instance: Optional["HistoryManager"] = None

    def __init__(self):
        self._entries: list[HistoryEntry] = []
        self._load()

    @classmethod
    def instance(cls) -> "HistoryManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def entries(self) -> list[HistoryEntry]:
        return self._entries

    @property
    def completed_entries(self) -> list[HistoryEntry]:
        return [e for e in self._entries if e.status == "Completed"]

    def add(self, entry: HistoryEntry):
        self._entries.insert(0, entry)
        self._save()

    def clear(self):
        self._entries.clear()
        self._save()

    def _save(self):
        os.makedirs(HISTORY_DIR, exist_ok=True)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(
                [asdict(e) for e in self._entries],
                f, indent=2, ensure_ascii=False
            )

    def _load(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._entries = [
                    HistoryEntry(**{
                        k: v for k, v in item.items()
                        if k in HistoryEntry.__dataclass_fields__
                    })
                    for item in data
                ]
            except (json.JSONDecodeError, TypeError):
                self._entries = []

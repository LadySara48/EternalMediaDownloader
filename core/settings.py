"""
✨ Eternal Media Downloader | Developed by Hearlov — Settings Manager
Persistent settings stored in data/settings.json
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


SETTINGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "settings.json")


@dataclass
class AppSettings:
    download_dir: str = ""
    speed_limit: int = 0
    max_parallel: int = 3
    default_format: str = "mp3"
    default_audio_quality: str = "128K"
    default_video_quality: str = "720p"

    def __post_init__(self):
        if not self.download_dir:
            self.download_dir = str(Path.home() / "Downloads" / "EternalMediaDownloader")


class SettingsManager:
    _instance: Optional["SettingsManager"] = None

    def __init__(self):
        self._settings = AppSettings()
        self._load()

    @classmethod
    def instance(cls) -> "SettingsManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def settings(self) -> AppSettings:
        return self._settings

    def save(self):
        os.makedirs(SETTINGS_DIR, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(asdict(self._settings), f, indent=2, ensure_ascii=False)

    def _load(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._settings = AppSettings(**{
                    k: v for k, v in data.items()
                    if k in AppSettings.__dataclass_fields__
                })
            except (json.JSONDecodeError, TypeError):
                self._settings = AppSettings()
        os.makedirs(self._settings.download_dir, exist_ok=True)

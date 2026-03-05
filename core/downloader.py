"""
✨ Eternal Media Downloader | Developed by Hearlov — Core Download Engine
yt-dlp subprocess wrapper with real-time progress parsing
"""

import subprocess
import shutil
import re
import os
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from PyQt6.QtCore import QObject, QThread, pyqtSignal

class DownloadStatus(Enum):
    QUEUED = "Queued"
    FETCHING_INFO = "Fetching Info"
    DOWNLOADING = "Downloading"
    CONVERTING = "Converting"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    ERROR = "Error"
    CANCELLED = "Cancelled"


class DownloadFormat(Enum):
    MP3_96K = ("mp3", "96K")
    MP3_128K = ("mp3", "128K")
    MP3_148K = ("mp3", "148K")
    VIDEO_360P = ("mp4", "360p")
    VIDEO_480P = ("mp4", "480p")
    VIDEO_720P = ("mp4", "720p")
    VIDEO_1080P = ("mp4", "1080p")

    @property
    def ext(self) -> str:
        return self.value[0]

    @property
    def quality(self) -> str:
        return self.value[1]

    @property
    def display_name(self) -> str:
        return f"{self.value[0].upper()} — {self.value[1]}"


@dataclass
class MediaInfo:
    title: str = "Unknown"
    duration: int = 0
    thumbnail: str = ""
    uploader: str = ""
    url: str = ""

    @property
    def duration_str(self) -> str:
        m, s = divmod(self.duration, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"


@dataclass
class DownloadProgress:
    percent: float = 0.0
    speed: str = "—"
    eta: str = "—"
    downloaded: str = "—"
    total_size: str = "—"
    status: DownloadStatus = DownloadStatus.QUEUED


def check_dependencies() -> dict[str, bool]:
    return {
        "yt-dlp": shutil.which("yt-dlp") is not None,
        "ffmpeg": shutil.which("ffmpeg") is not None,
    }


class InfoFetchWorker(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self._cancelled = False

    def run(self):
        try:
            cmd = [
                "yt-dlp",
                "--dump-json",
                "--no-playlist",
                "--no-warnings",
                self.url,
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )

            if self._cancelled:
                return

            if result.returncode != 0:
                self.error.emit(result.stderr.strip() or "Failed to fetch info")
                return

            data = json.loads(result.stdout)
            info = MediaInfo(
                title=data.get("title", "Unknown"),
                duration=int(data.get("duration", 0)),
                thumbnail=data.get("thumbnail", ""),
                uploader=data.get("uploader", ""),
                url=self.url,
            )
            self.finished.emit(info)

        except subprocess.TimeoutExpired:
            self.error.emit("Timeout: Could not fetch video info")
        except json.JSONDecodeError:
            self.error.emit("Failed to parse video info")
        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        self._cancelled = True

class DownloadWorker(QObject):
    progress = pyqtSignal(object)
    status_changed = pyqtSignal(object)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    _RE_PROGRESS = re.compile(
        r"\[download\]\s+(?P<percent>[\d.]+)%\s+of\s+~?\s*(?P<total>\S+)"
        r"\s+at\s+(?P<speed>\S+)\s+ETA\s+(?P<eta>\S+)"
    )
    _RE_PROGRESS_SIMPLE = re.compile(
        r"\[download\]\s+(?P<percent>[\d.]+)%"
    )
    _RE_DESTINATION = re.compile(
        r"\[download\]\s+Destination:\s+(?P<path>.+)"
    )
    _RE_ALREADY = re.compile(
        r"\[download\]\s+(?P<path>.+)\s+has already been downloaded"
    )
    _RE_MERGE = re.compile(
        r'\[Merger\]|Merging formats|\[ExtractAudio\]|\[ffmpeg\]'
    )

    def __init__(self, url: str, fmt: DownloadFormat, output_dir: str,
                 speed_limit: int = 0):
        super().__init__()
        self.url = url
        self.fmt = fmt
        self.output_dir = output_dir
        self.speed_limit = speed_limit
        self._process: Optional[subprocess.Popen] = None
        self._cancelled = False
        self._output_path = ""

    def run(self):
        try:
            cmd = self._build_command()
            self.status_changed.emit(DownloadStatus.DOWNLOADING)

            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )

            for line in iter(self._process.stdout.readline, ""):
                if self._cancelled:
                    self._process.terminate()
                    self.status_changed.emit(DownloadStatus.CANCELLED)
                    return

                line = line.strip()
                if not line:
                    continue

                self._parse_line(line)

            self._process.wait()

            if self._cancelled:
                self.status_changed.emit(DownloadStatus.CANCELLED)
                return

            if self._process.returncode == 0:
                self.status_changed.emit(DownloadStatus.COMPLETED)
                final = DownloadProgress(
                    percent=100.0,
                    speed="—",
                    eta="Done",
                    status=DownloadStatus.COMPLETED,
                )
                self.progress.emit(final)
                self.finished.emit(self._output_path)
            else:
                self.error.emit("Download failed with errors")

        except FileNotFoundError:
            self.error.emit("yt-dlp not found. Please install yt-dlp.")
        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        self._cancelled = True
        if self._process and self._process.poll() is None:
            self._process.terminate()

    def _build_command(self) -> list[str]:
        output_template = os.path.join(self.output_dir, "%(title)s.%(ext)s")
        cmd = [
            "yt-dlp",
            "--no-playlist",
            "--no-warnings",
            "--newline",
            "-o", output_template,
        ]
        if self.speed_limit > 0:
            cmd.extend(["-r", f"{self.speed_limit}K"])
        if self.fmt.ext == "mp3":
            bitrate = self.fmt.quality.replace("K", "")
            cmd.extend([
                "-x",
                "--audio-format", "mp3",
                "--audio-quality", f"{bitrate}K",
            ])
        else:
            height = self.fmt.quality.replace("p", "")
            cmd.extend([
                "-f", f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={height}]+bestaudio/best[height<={height}]",
                "--merge-output-format", "mp4",
                "--postprocessor-args", "ffmpeg:-c:v copy -c:a aac -b:a 192k",
            ])

        cmd.append(self.url)
        return cmd

    def _parse_line(self, line: str):
        m = self._RE_DESTINATION.match(line)
        if m:
            self._output_path = m.group("path")
            return

        m = self._RE_ALREADY.match(line)
        if m:
            self._output_path = m.group("path")
            return

        if self._RE_MERGE.search(line):
            self.status_changed.emit(DownloadStatus.CONVERTING)
            prog = DownloadProgress(
                percent=99.0,
                speed="—",
                eta="Converting...",
                status=DownloadStatus.CONVERTING,
            )
            self.progress.emit(prog)
            return

        m = self._RE_PROGRESS.search(line)
        if m:
            prog = DownloadProgress(
                percent=float(m.group("percent")),
                speed=m.group("speed"),
                eta=m.group("eta"),
                total_size=m.group("total"),
                status=DownloadStatus.DOWNLOADING,
            )
            self.progress.emit(prog)
            return

        m = self._RE_PROGRESS_SIMPLE.search(line)
        if m:
            prog = DownloadProgress(
                percent=float(m.group("percent")),
                status=DownloadStatus.DOWNLOADING,
            )
            self.progress.emit(prog)

class DownloadTask:

    def __init__(self, url: str, fmt: DownloadFormat, output_dir: str,
                 speed_limit: int = 0):
        self.url = url
        self.fmt = fmt
        self.output_dir = output_dir
        self.info: Optional[MediaInfo] = None
        self.status = DownloadStatus.QUEUED

        self._thread = QThread()
        self._worker = DownloadWorker(url, fmt, output_dir, speed_limit)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)

    @property
    def worker(self) -> DownloadWorker:
        return self._worker

    def start(self):
        self.status = DownloadStatus.DOWNLOADING
        self._thread.start()

    def cancel(self):
        self._worker.cancel()
        self.status = DownloadStatus.CANCELLED
        if self._thread.isRunning():
            self._thread.quit()
            self._thread.wait(3000)

    def is_running(self) -> bool:
        return self._thread.isRunning()

"""
✨ Eternal Media Downloader | Developed by Hearlov — Content Pages
All pages: Downloading, Completed, History, Settings
"""

import os
import sys
import uuid
import subprocess
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedWidget, QScrollArea, QMessageBox,
    QFileDialog, QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from ui.theme import COLORS, DIMS, FONTS
from core.downloader import (
    check_dependencies, InfoFetchWorker, DownloadTask,
    DownloadFormat, DownloadStatus, MediaInfo
)
from core.settings import SettingsManager
from core.history import HistoryManager, HistoryEntry


#  Shared Widgets
class URLInputBar(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(56)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self._input = QLineEdit()
        self._input.setPlaceholderText("🔗  Paste a URL here...")
        self._input.setFixedHeight(42)
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background: {COLORS["bg_tertiary"]};
                color: {COLORS["text_primary"]};
                border: 1px solid {COLORS["border"]};
                border-radius: {DIMS["border_radius_sm"]}px;
                padding: 0 16px;
                font-size: 13px;
                font-family: '{FONTS["primary"]}';
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS["accent"]};
            }}
            QLineEdit::placeholder {{
                color: {COLORS["text_muted"]};
            }}
        """)
        self._btn_download = QPushButton("⬇  Download")
        self._btn_download.setFixedSize(130, 42)
        self._btn_download.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_download.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS["accent"]};
                color: #FFFFFF;
                border: none;
                border-radius: {DIMS["border_radius_sm"]}px;
                font-size: 13px;
                font-weight: 600;
                font-family: '{FONTS["primary"]}';
            }}
            QPushButton:hover {{
                background: {COLORS["accent_hover"]};
            }}
            QPushButton:pressed {{
                background: {COLORS["accent"]};
            }}
        """)
        layout.addWidget(self._input, 1)
        layout.addWidget(self._btn_download)

    @property
    def download_button(self):
        return self._btn_download

    @property
    def url_input(self):
        return self._input


class EmptyState(QWidget):
    def __init__(self, icon: str, title: str, subtitle: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"font-size: 48px; color: {COLORS['text_muted']}; background: transparent;")
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont(FONTS["primary"], 16, QFont.Weight.DemiBold))
        title_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        sub_label = QLabel(subtitle)
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px; background: transparent;")
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(sub_label)

def _card_style() -> str:
    return f"""
        background: {COLORS["bg_card"]};
        border-radius: {DIMS["border_radius_sm"]}px;
        border: 1px solid {COLORS["border"]};
    """

def _section_label_style() -> str:
    return f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 600; background: transparent;"

def _small_btn_style(color: str = "") -> str:
    bg = color or COLORS["bg_tertiary"]
    return f"""
        QPushButton {{
            background: {bg};
            color: {COLORS["text_secondary"]};
            border: 1px solid {COLORS["border"]};
            border-radius: 6px;
            padding: 6px 14px;
            font-size: 12px;
        }}
        QPushButton:hover {{
            background: {COLORS["bg_hover"]};
            color: {COLORS["text_primary"]};
        }}
    """


#  Page: Downloading
class DownloadingPage(QWidget):

    download_completed = pyqtSignal(object)
    active_count_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks: dict[str, DownloadTask] = {}
        self._cards: dict = {}
        self._queue: list[str] = []
        self._active: set[str] = set()
        self._info_thread: QThread = None
        self._info_worker: InfoFetchWorker = None
        self._sm = SettingsManager.instance()
        os.makedirs(self._sm.settings.download_dir, exist_ok=True)
        self._setup_ui()
        self._check_deps()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)
        self.url_bar = URLInputBar()
        self.url_bar.download_button.clicked.connect(self._on_download_clicked)
        self.url_bar.url_input.returnPressed.connect(self._on_download_clicked)
        layout.addWidget(self.url_bar)
        self._status_label = QLabel("")
        self._status_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; background: transparent;")
        layout.addWidget(self._status_label)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self._cards_container = QWidget()
        self._cards_layout = QVBoxLayout(self._cards_container)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(8)
        self._cards_layout.addStretch()
        scroll.setWidget(self._cards_container)
        self._stack = QStackedWidget()
        self._empty = EmptyState("⬇", "No active downloads", "Paste a URL above to start downloading")
        self._stack.addWidget(self._empty)
        self._stack.addWidget(scroll)
        layout.addWidget(self._stack, 1)

    def _check_deps(self):
        deps = check_dependencies()
        missing = [k for k, v in deps.items() if not v]
        if missing:
            self._status_label.setText(f"⚠ Missing: {', '.join(missing)} — Please install before downloading")
            self._status_label.setStyleSheet(f"color: {COLORS['warning']}; font-size: 11px; background: transparent;")

    def _on_download_clicked(self):
        url = self.url_bar.url_input.text().strip()
        if not url:
            return

        deps = check_dependencies()
        missing = [k for k, v in deps.items() if not v]
        if missing:
            QMessageBox.warning(
                self, "Missing Dependencies",
                f"Please install: {', '.join(missing)}\n\n"
                f"yt-dlp: pip install yt-dlp\n"
                f"ffmpeg: https://ffmpeg.org/download.html"
            )
            return

        self.url_bar.download_button.setEnabled(False)
        self._status_label.setText("⏳ Fetching video info...")
        self._status_label.setStyleSheet(f"color: {COLORS['info']}; font-size: 11px; background: transparent;")
        self._info_thread = QThread()
        self._info_worker = InfoFetchWorker(url)
        self._info_worker.moveToThread(self._info_thread)
        self._info_thread.started.connect(self._info_worker.run)
        self._info_worker.finished.connect(self._on_info_fetched)
        self._info_worker.error.connect(self._on_info_error)
        self._info_worker.finished.connect(self._info_thread.quit)
        self._info_worker.error.connect(self._info_thread.quit)
        self._info_thread.start()

    def _on_info_fetched(self, info: MediaInfo):
        self.url_bar.download_button.setEnabled(True)
        self._status_label.setText("")
        from ui.format_dialog import FormatDialog
        dialog = FormatDialog(info, self.window())
        if dialog.exec():
            self._start_download(info, dialog.selected_format)
            self.url_bar.url_input.clear()

    def _on_info_error(self, error_msg: str):
        self.url_bar.download_button.setEnabled(True)
        self._status_label.setText(f"✕ {error_msg}")
        self._status_label.setStyleSheet(f"color: {COLORS['error']}; font-size: 11px; background: transparent;")

    def _start_download(self, info: MediaInfo, fmt: DownloadFormat):
        from ui.download_card import DownloadCard
        task_id = str(uuid.uuid4())[:8]
        settings = self._sm.settings
        output_dir = settings.download_dir
        os.makedirs(output_dir, exist_ok=True)
        task = DownloadTask(info.url, fmt, output_dir, settings.speed_limit)
        task.info = info
        self._tasks[task_id] = task
        card = DownloadCard(task_id, info, fmt)
        card.cancel_requested.connect(self._on_cancel_task)
        self._cards[task_id] = card
        self._cards_layout.insertWidget(0, card)
        self._stack.setCurrentIndex(1)
        task.worker.progress.connect(lambda prog, c=card: c.update_progress(prog))
        task.worker.status_changed.connect(lambda st, c=card: c.update_status(st))
        task.worker.error.connect(lambda err, c=card: c.set_error(err))
        task.worker.finished.connect(lambda path, c=card: c.set_output_path(path))
        task.worker.finished.connect(
            lambda path, i=info, f=fmt: self._on_download_finished(i, f, path)
        )
        task.worker.error.connect(
            lambda err, i=info, f=fmt: self._on_download_error(i, f, err)
        )
        task.worker.finished.connect(lambda _path, tid=task_id: self._on_task_done(tid))
        task.worker.error.connect(lambda _err, tid=task_id: self._on_task_done(tid))
        max_parallel = self._sm.settings.max_parallel
        if len(self._active) < max_parallel:
            self._active.add(task_id)
            task.start()
            self._update_queue_status()
        else:
            self._queue.append(task_id)
            card.update_status(DownloadStatus.QUEUED)
            self._update_queue_status()

    def _on_task_done(self, task_id: str):
        self._active.discard(task_id)
        self._process_queue()

    def _process_queue(self):
        max_parallel = self._sm.settings.max_parallel
        while self._queue and len(self._active) < max_parallel:
            next_id = self._queue.pop(0)
            task = self._tasks.get(next_id)
            if task and task.status != DownloadStatus.CANCELLED:
                self._active.add(next_id)
                task.start()
        self._update_queue_status()

    def _update_queue_status(self):
        total_active = len(self._active) + len(self._queue)
        self.active_count_changed.emit(total_active)

        if self._queue:
            self._status_label.setText(
                f"📋 {len(self._active)} active, {len(self._queue)} in queue"
            )
            self._status_label.setStyleSheet(
                f"color: {COLORS['info']}; font-size: 11px; background: transparent;"
            )
        elif self._active:
            self._status_label.setText(f"⬇ {len(self._active)} active download(s)")
            self._status_label.setStyleSheet(
                f"color: {COLORS['info']}; font-size: 11px; background: transparent;"
            )
        else:
            self._status_label.setText("")

    def _on_cancel_task(self, task_id: str):
        task = self._tasks.get(task_id)
        if task:
            task.cancel()
        if task_id in self._queue:
            self._queue.remove(task_id)
        self._active.discard(task_id)
        self._process_queue()

    def _on_download_finished(self, info: MediaInfo, fmt: DownloadFormat, path: str):
        entry = HistoryEntry(
            title=info.title,
            url=info.url,
            format_type=fmt.ext,
            quality=fmt.quality,
            file_path=path,
            status="Completed",
            uploader=info.uploader,
        )
        HistoryManager.instance().add(entry)
        self.download_completed.emit(entry)

    def _on_download_error(self, info: MediaInfo, fmt: DownloadFormat, error: str):
        entry = HistoryEntry(
            title=info.title,
            url=info.url,
            format_type=fmt.ext,
            quality=fmt.quality,
            file_path="",
            status="Error",
            uploader=info.uploader,
        )
        HistoryManager.instance().add(entry)

#  Page: Completed
class CompletedCard(QWidget):

    def __init__(self, entry: HistoryEntry, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.setFixedHeight(72)
        self._setup_ui()

    @staticmethod
    def _format_size(path: str) -> str:
        try:
            size = os.path.getsize(path)
            for unit in ("B", "KB", "MB", "GB"):
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} TB"
        except (OSError, FileNotFoundError):
            return "—"

    def _setup_ui(self):
        self.setStyleSheet(_card_style())
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 12, 10)
        layout.setSpacing(12)
        icon = "♫" if self.entry.format_type == "mp3" else "▶"
        icon_label = QLabel(icon)
        icon_label.setFixedWidth(28)
        icon_label.setStyleSheet(f"font-size: 20px; color: {COLORS['accent']}; background: transparent;")
        layout.addWidget(icon_label)
        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        title = QLabel(self.entry.title)
        title.setFont(QFont(FONTS["primary"], 11, QFont.Weight.DemiBold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        file_size = self._format_size(self.entry.file_path) if self.entry.file_path else "—"
        meta = QLabel(f"{self.entry.quality}  •  {file_size}  •  {self.entry.date}")
        meta.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; background: transparent;")
        info_col.addWidget(title)
        info_col.addWidget(meta)
        layout.addLayout(info_col, 1)
        btn_folder = QPushButton("📁")
        btn_folder.setFixedSize(32, 32)
        btn_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_folder.setToolTip("Open folder")
        btn_folder.setStyleSheet(_small_btn_style())
        btn_folder.clicked.connect(self._open_folder)
        layout.addWidget(btn_folder)
        btn_open = QPushButton("▶")
        btn_open.setFixedSize(32, 32)
        btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open.setToolTip("Open file")
        btn_open.setStyleSheet(_small_btn_style())
        btn_open.clicked.connect(self._open_file)
        layout.addWidget(btn_open)

    def _open_folder(self):
        folder = os.path.dirname(self.entry.file_path)
        if os.path.isdir(folder):
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])

    def _open_file(self):
        if os.path.isfile(self.entry.file_path):
            if sys.platform == "win32":
                os.startfile(self.entry.file_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.entry.file_path])
            else:
                subprocess.Popen(["xdg-open", self.entry.file_path])


class CompletedPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_existing()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)
        header_row = QHBoxLayout()
        header = QLabel("✓  Completed Downloads")
        header.setFont(QFont(FONTS["primary"], 16, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        header_row.addWidget(header)
        header_row.addStretch()
        layout.addLayout(header_row)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self._cards_container = QWidget()
        self._cards_layout = QVBoxLayout(self._cards_container)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(6)
        self._cards_layout.addStretch()
        scroll.setWidget(self._cards_container)
        self._stack = QStackedWidget()
        self._empty = EmptyState("✓", "No completed downloads", "Completed downloads will appear here")
        self._stack.addWidget(self._empty)
        self._stack.addWidget(scroll)
        layout.addWidget(self._stack, 1)

    def _load_existing(self):
        hm = HistoryManager.instance()
        for entry in hm.completed_entries:
            self._add_card(entry)

    def add_entry(self, entry: HistoryEntry):
        self._add_card(entry)

    def _add_card(self, entry: HistoryEntry):
        card = CompletedCard(entry)
        self._cards_layout.insertWidget(0, card)
        self._stack.setCurrentIndex(1)


#  Page: History
class HistoryRow(QWidget):

    redownload = pyqtSignal(str)

    def __init__(self, entry: HistoryEntry, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.setFixedHeight(52)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_card_style())
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 12, 8)
        layout.setSpacing(10)
        status_color = COLORS["success"] if self.entry.status == "Completed" else COLORS["error"]
        dot = QLabel("●")
        dot.setFixedWidth(16)
        dot.setStyleSheet(f"color: {status_color}; font-size: 8px; background: transparent;")
        layout.addWidget(dot)
        title = QLabel(self.entry.title)
        title.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; background: transparent;")
        layout.addWidget(title, 1)
        badge = QLabel(f"{self.entry.format_type.upper()} {self.entry.quality}")
        badge.setStyleSheet(f"""
            background: {COLORS["bg_tertiary"]};
            color: {COLORS["text_muted"]};
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 10px;
        """)
        layout.addWidget(badge)
        date_label = QLabel(self.entry.date)
        date_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; background: transparent;")
        layout.addWidget(date_label)
        btn_re = QPushButton("⟳")
        btn_re.setFixedSize(28, 28)
        btn_re.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_re.setToolTip("Download again")
        btn_re.setStyleSheet(_small_btn_style())
        btn_re.clicked.connect(lambda: self.redownload.emit(self.entry.url))
        layout.addWidget(btn_re)


class HistoryPage(QWidget):

    redownload_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_rows: list[HistoryRow] = []
        self._setup_ui()
        self._load_existing()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)
        header_row = QHBoxLayout()
        header = QLabel("◷  Download History")
        header.setFont(QFont(FONTS["primary"], 16, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        header_row.addWidget(header)
        header_row.addStretch()
        self._btn_clear = QPushButton("Clear History")
        self._btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_clear.setStyleSheet(_small_btn_style())
        self._btn_clear.clicked.connect(self._on_clear)
        header_row.addWidget(self._btn_clear)
        layout.addLayout(header_row)
        search_row = QHBoxLayout()
        search_row.setSpacing(8)
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("🔍  Search history...")
        self._search_input.setFixedHeight(34)
        self._search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {COLORS["bg_tertiary"]};
                color: {COLORS["text_primary"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 6px;
                padding: 0 12px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS["accent"]};
            }}
            QLineEdit::placeholder {{
                color: {COLORS["text_muted"]};
            }}
        """)
        self._search_input.textChanged.connect(self._on_search)
        search_row.addWidget(self._search_input, 1)
        self._filter_all = self._create_filter_btn("All", active=True)
        self._filter_mp3 = self._create_filter_btn("MP3")
        self._filter_mp4 = self._create_filter_btn("MP4")
        self._filter_all.clicked.connect(lambda: self._on_filter("all"))
        self._filter_mp3.clicked.connect(lambda: self._on_filter("mp3"))
        self._filter_mp4.clicked.connect(lambda: self._on_filter("mp4"))
        search_row.addWidget(self._filter_all)
        search_row.addWidget(self._filter_mp3)
        search_row.addWidget(self._filter_mp4)
        layout.addLayout(search_row)
        self._active_filter = "all"
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self._rows_container = QWidget()
        self._rows_layout = QVBoxLayout(self._rows_container)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(4)
        self._rows_layout.addStretch()
        scroll.setWidget(self._rows_container)
        self._stack = QStackedWidget()
        self._empty = EmptyState("◷", "No download history", "Your download history will be saved here")
        self._stack.addWidget(self._empty)
        self._stack.addWidget(scroll)
        layout.addWidget(self._stack, 1)

    def _create_filter_btn(self, text: str, active: bool = False) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedHeight(34)
        btn.setFixedWidth(50)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setCheckable(True)
        btn.setChecked(active)
        self._style_filter_btn(btn, active)
        return btn

    def _style_filter_btn(self, btn: QPushButton, active: bool):
        if active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLORS["accent_light"]};
                    color: {COLORS["accent"]};
                    border: 1px solid {COLORS["accent"]};
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 600;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLORS["bg_tertiary"]};
                    color: {COLORS["text_muted"]};
                    border: 1px solid {COLORS["border"]};
                    border-radius: 6px;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background: {COLORS["bg_hover"]};
                }}
            """)

    def _on_filter(self, filter_type: str):
        self._active_filter = filter_type
        for btn, name in [(self._filter_all, "all"), (self._filter_mp3, "mp3"), (self._filter_mp4, "mp4")]:
            btn.setChecked(name == filter_type)
            self._style_filter_btn(btn, name == filter_type)
        self._apply_filters()

    def _on_search(self, text: str):
        self._apply_filters()

    def _apply_filters(self):
        search_text = self._search_input.text().lower().strip()
        for row in self._all_rows:
            visible = True
            if self._active_filter != "all" and row.entry.format_type != self._active_filter:
                visible = False
            if search_text and search_text not in row.entry.title.lower():
                visible = False
            row.setVisible(visible)

    def _load_existing(self):
        hm = HistoryManager.instance()
        for entry in hm.entries:
            self._add_row(entry)

    def add_entry(self, entry: HistoryEntry):
        self._add_row(entry)

    def _add_row(self, entry: HistoryEntry):
        row = HistoryRow(entry)
        row.redownload.connect(self.redownload_requested.emit)
        self._all_rows.append(row)
        self._rows_layout.insertWidget(0, row)
        self._stack.setCurrentIndex(1)

    def _on_clear(self):
        reply = QMessageBox.question(
            self, "Clear History",
            "Are you sure you want to clear all download history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            HistoryManager.instance().clear()
            self._all_rows.clear()
            while self._rows_layout.count() > 1:
                item = self._rows_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self._stack.setCurrentIndex(0)

#  Page: Settings
class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._sm = SettingsManager.instance()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(20)
        header = QLabel("⚙  Settings")
        header.setFont(QFont(FONTS["primary"], 18, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        layout.addWidget(header)
        layout.addWidget(self._section_label("Download Directory"))
        dir_row = QHBoxLayout()
        dir_row.setSpacing(10)
        self._dir_input = QLineEdit(self._sm.settings.download_dir)
        self._dir_input.setFixedHeight(38)
        self._dir_input.setReadOnly(True)
        self._dir_input.setStyleSheet(self._input_style())
        dir_row.addWidget(self._dir_input, 1)
        btn_browse = QPushButton("Browse...")
        btn_browse.setFixedHeight(38)
        btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse.setStyleSheet(_small_btn_style())
        btn_browse.clicked.connect(self._on_browse)
        dir_row.addWidget(btn_browse)
        layout.addLayout(dir_row)
        layout.addWidget(self._section_label("Default Speed Limit"))
        speed_row = QHBoxLayout()
        speed_row.setSpacing(10)
        self._speed_input = QSpinBox()
        self._speed_input.setRange(0, 100000)
        self._speed_input.setValue(self._sm.settings.speed_limit)
        self._speed_input.setSuffix(" KB/s")
        self._speed_input.setSpecialValueText("Unlimited")
        self._speed_input.setFixedHeight(38)
        self._speed_input.setFixedWidth(180)
        self._speed_input.setStyleSheet(self._spinbox_style())
        speed_row.addWidget(self._speed_input)
        speed_hint = QLabel("0 = Unlimited")
        speed_hint.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; background: transparent;")
        speed_row.addWidget(speed_hint)
        speed_row.addStretch()
        layout.addLayout(speed_row)
        layout.addWidget(self._section_label("Maximum Parallel Downloads"))
        parallel_row = QHBoxLayout()
        parallel_row.setSpacing(10)
        self._parallel_input = QSpinBox()
        self._parallel_input.setRange(1, 10)
        self._parallel_input.setValue(self._sm.settings.max_parallel)
        self._parallel_input.setFixedHeight(38)
        self._parallel_input.setFixedWidth(100)
        self._parallel_input.setStyleSheet(self._spinbox_style())
        parallel_row.addWidget(self._parallel_input)
        parallel_row.addStretch()
        layout.addLayout(parallel_row)
        layout.addWidget(self._section_label("Default Format"))
        format_row = QHBoxLayout()
        format_row.setSpacing(10)
        self._format_combo = QComboBox()
        self._format_combo.addItems(["mp3", "mp4"])
        self._format_combo.setCurrentText(self._sm.settings.default_format)
        self._format_combo.setFixedHeight(38)
        self._format_combo.setFixedWidth(120)
        self._format_combo.setStyleSheet(self._combo_style())
        format_row.addWidget(self._format_combo)
        format_row.addStretch()
        layout.addLayout(format_row)
        layout.addWidget(self._section_label("Default Audio Quality"))
        aq_row = QHBoxLayout()
        self._audio_q_combo = QComboBox()
        self._audio_q_combo.addItems(["96K", "128K", "148K"])
        self._audio_q_combo.setCurrentText(self._sm.settings.default_audio_quality)
        self._audio_q_combo.setFixedHeight(38)
        self._audio_q_combo.setFixedWidth(120)
        self._audio_q_combo.setStyleSheet(self._combo_style())
        aq_row.addWidget(self._audio_q_combo)
        aq_row.addStretch()
        layout.addLayout(aq_row)
        layout.addWidget(self._section_label("Default Video Quality"))
        vq_row = QHBoxLayout()
        self._video_q_combo = QComboBox()
        self._video_q_combo.addItems(["360p", "480p", "720p", "1080p"])
        self._video_q_combo.setCurrentText(self._sm.settings.default_video_quality)
        self._video_q_combo.setFixedHeight(38)
        self._video_q_combo.setFixedWidth(120)
        self._video_q_combo.setStyleSheet(self._combo_style())
        vq_row.addWidget(self._video_q_combo)
        vq_row.addStretch()
        layout.addLayout(vq_row)
        layout.addStretch()
        save_row = QHBoxLayout()
        save_row.addStretch()
        btn_save = QPushButton("💾  Save Settings")
        btn_save.setFixedHeight(42)
        btn_save.setFixedWidth(180)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS["accent"]};
                color: #FFFFFF;
                border: none;
                border-radius: {DIMS["border_radius_sm"]}px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {COLORS["accent_hover"]};
            }}
        """)
        btn_save.clicked.connect(self._on_save)
        save_row.addWidget(btn_save)
        layout.addLayout(save_row)
        layout.addSpacing(12)
        about_container = QWidget()
        about_container.setStyleSheet(f"""
            background: {COLORS["bg_tertiary"]};
            border-radius: {DIMS["border_radius_sm"]}px;
            border: 1px solid {COLORS["border"]};
        """)
        about_layout = QVBoxLayout(about_container)
        about_layout.setContentsMargins(16, 12, 16, 12)
        about_layout.setSpacing(6)
        about_title = QLabel("✦  Eternal Media Downloader")
        about_title.setFont(QFont(FONTS["primary"], 13, QFont.Weight.Bold))
        about_title.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")
        about_dev = QLabel("Developed with 💜 by Hearlov")
        about_dev.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 12px; background: transparent;")
        about_ver = QLabel("v1.0  •  github.com/LadySara48  •  MIT License")
        about_ver.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; background: transparent;")
        about_layout.addWidget(about_title)
        about_layout.addWidget(about_dev)
        about_layout.addWidget(about_ver)
        layout.addWidget(about_container)

    def _section_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(_section_label_style())
        return label

    def _input_style(self) -> str:
        return f"""
            QLineEdit {{
                background: {COLORS["bg_tertiary"]};
                color: {COLORS["text_primary"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 6px;
                padding: 0 12px;
                font-size: 12px;
            }}
        """

    def _spinbox_style(self) -> str:
        return f"""
            QSpinBox {{
                background: {COLORS["bg_tertiary"]};
                color: {COLORS["text_primary"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 6px;
                padding: 0 12px;
                font-size: 12px;
            }}
            QSpinBox:focus {{
                border: 1px solid {COLORS["accent"]};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 20px;
                background: {COLORS["bg_hover"]};
                border: none;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background: {COLORS["bg_active"]};
            }}
        """

    def _combo_style(self) -> str:
        return f"""
            QComboBox {{
                background: {COLORS["bg_tertiary"]};
                color: {COLORS["text_primary"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 6px;
                padding: 0 12px;
                font-size: 12px;
            }}
            QComboBox:focus {{
                border: 1px solid {COLORS["accent"]};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 28px;
            }}
            QComboBox QAbstractItemView {{
                background: {COLORS["bg_card"]};
                color: {COLORS["text_primary"]};
                border: 1px solid {COLORS["border"]};
                selection-background-color: {COLORS["accent_light"]};
                selection-color: {COLORS["accent"]};
            }}
        """

    def _on_browse(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Download Directory",
            self._sm.settings.download_dir
        )
        if folder:
            self._dir_input.setText(folder)

    def _on_save(self):
        s = self._sm.settings
        s.download_dir = self._dir_input.text()
        s.speed_limit = self._speed_input.value()
        s.max_parallel = self._parallel_input.value()
        s.default_format = self._format_combo.currentText()
        s.default_audio_quality = self._audio_q_combo.currentText()
        s.default_video_quality = self._video_q_combo.currentText()

        os.makedirs(s.download_dir, exist_ok=True)
        self._sm.save()

        QMessageBox.information(self, "Settings", "Settings saved successfully! ✓")

#  Content Stack
class ContentStack(QStackedWidget):

    PAGE_MAP = {
        "Downloading": 0,
        "Completed": 1,
        "History": 2,
        "Settings": 3,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.downloading_page = DownloadingPage()
        self.completed_page = CompletedPage()
        self.history_page = HistoryPage()
        self.settings_page = SettingsPage()
        self.addWidget(self.downloading_page)
        self.addWidget(self.completed_page)
        self.addWidget(self.history_page)
        self.addWidget(self.settings_page)
        self.downloading_page.download_completed.connect(self.completed_page.add_entry)
        self.downloading_page.download_completed.connect(self.history_page.add_entry)
        self.history_page.redownload_requested.connect(self._on_redownload)

    def switch_to(self, section: str):
        idx = self.PAGE_MAP.get(section, 0)
        self.setCurrentIndex(idx)

    def _on_redownload(self, url: str):
        self.downloading_page.url_bar.url_input.setText(url)
        self.setCurrentIndex(0)

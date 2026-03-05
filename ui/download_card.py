"""
✨ Eternal Media Downloader | Developed by Hearlov — Download Card Widget
Individual download card showing progress, speed, ETA, and controls
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ui.theme import COLORS, DIMS, FONTS
from core.downloader import DownloadProgress, DownloadStatus, DownloadFormat, MediaInfo


class DownloadCard(QWidget):
    cancel_requested = pyqtSignal(str)

    def __init__(self, task_id: str, info: MediaInfo, fmt: DownloadFormat, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.info = info
        self.fmt = fmt
        self._status = DownloadStatus.QUEUED

        self.setFixedHeight(100)
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        self._title_label = QLabel(self.info.title)
        self._title_label.setFont(QFont(FONTS["primary"], 12, QFont.Weight.DemiBold))
        self._title_label.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        self._title_label.setMaximumWidth(500)
        self._format_badge = QLabel(self.fmt.display_name)
        self._format_badge.setFixedHeight(22)
        self._format_badge.setStyleSheet(f"""
            background: {COLORS["accent_light"]};
            color: {COLORS["accent"]};
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: 600;
        """)

        self._status_label = QLabel(self._status.value)
        self._status_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; background: transparent;")

        self._btn_cancel = QPushButton("✕")
        self._btn_cancel.setFixedSize(28, 28)
        self._btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_cancel.setToolTip("Cancel download")
        self._btn_cancel.clicked.connect(lambda: self.cancel_requested.emit(self.task_id))
        self._btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS["text_muted"]};
                border: none;
                border-radius: 6px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {COLORS["error"]}33;
                color: {COLORS["error"]};
            }}
        """)

        top_row.addWidget(self._title_label, 1)
        top_row.addWidget(self._format_badge)
        top_row.addWidget(self._status_label)
        top_row.addWidget(self._btn_cancel)

        layout.addLayout(top_row)

        self._progress_bar = QProgressBar()
        self._progress_bar.setFixedHeight(6)
        self._progress_bar.setRange(0, 1000)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background: {COLORS["bg_tertiary"]};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS["accent"]},
                    stop:1 {COLORS["accent_hover"]}
                );
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self._progress_bar)
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(16)
        self._speed_label = QLabel("Speed: —")
        self._speed_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; background: transparent;")
        self._eta_label = QLabel("ETA: —")
        self._eta_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; background: transparent;")
        self._percent_label = QLabel("0%")
        self._percent_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._percent_label.setFont(QFont(FONTS["primary"], 11, QFont.Weight.Bold))
        self._percent_label.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")
        bottom_row.addWidget(self._speed_label)
        bottom_row.addWidget(self._eta_label)
        bottom_row.addStretch()
        bottom_row.addWidget(self._percent_label)
        layout.addLayout(bottom_row)
        self._path_label = QLabel("")
        self._path_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; background: transparent;")
        self._path_label.setWordWrap(True)
        self._path_label.setVisible(False)
        layout.addWidget(self._path_label)

    def _apply_style(self):
        self.setStyleSheet(f"""
            DownloadCard {{
                background: {COLORS["bg_card"]};
                border-radius: {DIMS["border_radius_sm"]}px;
                border: 1px solid {COLORS["border"]};
            }}
        """)

    def update_progress(self, prog: DownloadProgress):
        self._progress_bar.setValue(int(prog.percent * 10))
        self._percent_label.setText(f"{prog.percent:.1f}%")
        self._speed_label.setText(f"Speed: {prog.speed}")
        self._eta_label.setText(f"ETA: {prog.eta}")

    def update_status(self, status: DownloadStatus):
        self._status = status
        self._status_label.setText(status.value)
        color_map = {
            DownloadStatus.QUEUED: COLORS["text_muted"],
            DownloadStatus.FETCHING_INFO: COLORS["info"],
            DownloadStatus.DOWNLOADING: COLORS["info"],
            DownloadStatus.CONVERTING: COLORS["warning"],
            DownloadStatus.COMPLETED: COLORS["success"],
            DownloadStatus.ERROR: COLORS["error"],
            DownloadStatus.CANCELLED: COLORS["text_muted"],
        }
        color = color_map.get(status, COLORS["text_muted"])
        self._status_label.setStyleSheet(f"color: {color}; font-size: 11px; background: transparent;")
        if status == DownloadStatus.COMPLETED:
            self._progress_bar.setValue(1000)
            self._percent_label.setText("100%")
            self._speed_label.setText("Speed: —")
            self._eta_label.setText("Done ✓")
            self._percent_label.setStyleSheet(f"color: {COLORS['success']}; background: transparent;")
            self._btn_cancel.setVisible(False)
            self.setFixedHeight(120)
            self._progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    background: {COLORS["bg_tertiary"]};
                    border: none;
                    border-radius: 3px;
                }}
                QProgressBar::chunk {{
                    background: {COLORS["success"]};
                    border-radius: 3px;
                }}
            """)
        elif status in (DownloadStatus.ERROR, DownloadStatus.CANCELLED):
            self._btn_cancel.setVisible(False)
            self._speed_label.setText("Speed: —")
            self._eta_label.setText("—")

    def set_error(self, message: str):
        self.update_status(DownloadStatus.ERROR)
        self._eta_label.setText(message[:50])

    def set_output_path(self, path: str):
        self._path_label.setText(f"📁  {path}")
        self._path_label.setVisible(True)

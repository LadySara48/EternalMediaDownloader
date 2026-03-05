"""
✨ Eternal Media Downloader | Developed by Hearlov — Format Selection Dialog
Modern popup dialog for choosing download format & quality
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QButtonGroup, QRadioButton, QWidget, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

from ui.theme import COLORS, DIMS, FONTS
from core.downloader import DownloadFormat, MediaInfo
from core.settings import SettingsManager

_AUDIO_QUALITY_MAP = {"96K": DownloadFormat.MP3_96K, "128K": DownloadFormat.MP3_128K, "148K": DownloadFormat.MP3_148K}
_VIDEO_QUALITY_MAP = {"360p": DownloadFormat.VIDEO_360P, "480p": DownloadFormat.VIDEO_480P, "720p": DownloadFormat.VIDEO_720P, "1080p": DownloadFormat.VIDEO_1080P}


class FormatDialog(QDialog):

    def __init__(self, info: MediaInfo, parent=None):
        super().__init__(parent)
        self.info = info
        self._sm = SettingsManager.instance()
        s = self._sm.settings
        if s.default_format == "mp3":
            self.selected_format = _AUDIO_QUALITY_MAP.get(s.default_audio_quality, DownloadFormat.MP3_128K)
        else:
            self.selected_format = _VIDEO_QUALITY_MAP.get(s.default_video_quality, DownloadFormat.VIDEO_720P)
        self.setWindowTitle("Download Options")
        self.setFixedSize(420, 520)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._setup_ui()

    def _setup_ui(self):
        container = QWidget(self)
        container.setGeometry(10, 10, 400, 500)
        container.setObjectName("FormatDialogContainer")
        container.setStyleSheet(f"""
            #FormatDialogContainer {{
                background: {COLORS["bg_secondary"]};
                border-radius: {DIMS["border_radius"]}px;
                border: 1px solid {COLORS["border"]};
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 120))
        container.setGraphicsEffect(shadow)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        title = QLabel("⬇  Download Options")
        title.setFont(QFont(FONTS["primary"], 15, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        layout.addWidget(title)
        info_widget = QWidget()
        info_widget.setStyleSheet(f"""
            background: {COLORS["bg_tertiary"]};
            border-radius: {DIMS["border_radius_sm"]}px;
            padding: 4px;
        """)
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(14, 10, 14, 10)
        info_layout.setSpacing(4)
        media_title = QLabel(self.info.title)
        media_title.setFont(QFont(FONTS["primary"], 12, QFont.Weight.DemiBold))
        media_title.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        media_title.setWordWrap(True)
        media_title.setMaximumHeight(40)
        media_meta = QLabel(f"{self.info.uploader}  •  {self.info.duration_str}")
        media_meta.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; background: transparent;")
        info_layout.addWidget(media_title)
        info_layout.addWidget(media_meta)
        layout.addWidget(info_widget)
        type_label = QLabel("Format")
        type_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 600; background: transparent;")
        layout.addWidget(type_label)
        type_row = QHBoxLayout()
        type_row.setSpacing(8)
        self._btn_audio = self._create_toggle_btn("♫  Audio (MP3)", self._sm.settings.default_format == "mp3")
        self._btn_video = self._create_toggle_btn("▶  Video (MP4)", self._sm.settings.default_format == "mp4")
        self._btn_audio.clicked.connect(lambda: self._switch_type("audio"))
        self._btn_video.clicked.connect(lambda: self._switch_type("video"))
        type_row.addWidget(self._btn_audio)
        type_row.addWidget(self._btn_video)
        layout.addLayout(type_row)
        quality_label = QLabel("Quality")
        quality_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 600; background: transparent;")
        layout.addWidget(quality_label)
        self._quality_group = QButtonGroup(self)
        self._quality_container = QWidget()
        self._quality_layout = QVBoxLayout(self._quality_container)
        self._quality_layout.setContentsMargins(0, 0, 0, 0)
        self._quality_layout.setSpacing(4)
        layout.addWidget(self._quality_container)
        self._populate_quality("audio" if self._sm.settings.default_format == "mp3" else "video")
        layout.addStretch()
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS["bg_tertiary"]};
                color: {COLORS["text_secondary"]};
                border: 1px solid {COLORS["border"]};
                border-radius: {DIMS["border_radius_sm"]}px;
                font-size: 13px;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background: {COLORS["bg_hover"]};
                color: {COLORS["text_primary"]};
            }}
        """)
        btn_start = QPushButton("⬇  Start Download")
        btn_start.setFixedHeight(38)
        btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_start.clicked.connect(self._on_start)
        btn_start.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS["accent"]};
                color: #FFFFFF;
                border: none;
                border-radius: {DIMS["border_radius_sm"]}px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 24px;
            }}
            QPushButton:hover {{
                background: {COLORS["accent_hover"]};
            }}
        """)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_start, 1)
        layout.addLayout(btn_row)
        
    def _create_toggle_btn(self, text: str, active: bool) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedHeight(36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setCheckable(True)
        btn.setChecked(active)
        self._style_toggle_btn(btn, active)
        return btn

    def _style_toggle_btn(self, btn: QPushButton, active: bool):
        if active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLORS["accent_light"]};
                    color: {COLORS["accent"]};
                    border: 1px solid {COLORS["accent"]};
                    border-radius: {DIMS["border_radius_sm"]}px;
                    font-size: 12px;
                    font-weight: 600;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLORS["bg_tertiary"]};
                    color: {COLORS["text_secondary"]};
                    border: 1px solid {COLORS["border"]};
                    border-radius: {DIMS["border_radius_sm"]}px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background: {COLORS["bg_hover"]};
                }}
            """)

    def _switch_type(self, fmt_type: str):
        is_audio = fmt_type == "audio"
        self._btn_audio.setChecked(is_audio)
        self._btn_video.setChecked(not is_audio)
        self._style_toggle_btn(self._btn_audio, is_audio)
        self._style_toggle_btn(self._btn_video, not is_audio)
        self._populate_quality(fmt_type)

    def _populate_quality(self, fmt_type: str):
        for btn in self._quality_group.buttons():
            self._quality_group.removeButton(btn)
            btn.deleteLater()

        while self._quality_layout.count():
            item = self._quality_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if fmt_type == "audio":
            options = [
                (DownloadFormat.MP3_96K, "96K  —  Lower quality, smaller file"),
                (DownloadFormat.MP3_128K, "128K  —  Standard quality ✦"),
                (DownloadFormat.MP3_148K, "148K  —  Higher quality"),
            ]
            default_quality = self._sm.settings.default_audio_quality
        else:
            options = [
                (DownloadFormat.VIDEO_360P, "360p  —  Low quality"),
                (DownloadFormat.VIDEO_480P, "480p  —  Medium quality"),
                (DownloadFormat.VIDEO_720P, "720p  —  HD ✦"),
                (DownloadFormat.VIDEO_1080P, "1080p  —  Full HD"),
            ]
            default_quality = self._sm.settings.default_video_quality
        for i, (fmt, label) in enumerate(options):
            radio = QRadioButton(label)
            radio.setStyleSheet(f"""
                QRadioButton {{
                    color: {COLORS["text_primary"]};
                    font-size: 12px;
                    spacing: 8px;
                    padding: 6px 4px;
                    background: transparent;
                }}
                QRadioButton::indicator {{
                    width: 14px;
                    height: 14px;
                }}
                QRadioButton::indicator:checked {{
                    background: {COLORS["accent"]};
                    border: 2px solid {COLORS["accent"]};
                    border-radius: 7px;
                }}
                QRadioButton::indicator:unchecked {{
                    background: transparent;
                    border: 2px solid {COLORS["text_muted"]};
                    border-radius: 7px;
                }}
            """)
            if fmt.quality == default_quality:
                radio.setChecked(True)
                self.selected_format = fmt
            radio.fmt = fmt  # Store format on widget
            radio.toggled.connect(lambda checked, f=fmt: self._on_quality_changed(f, checked))
            self._quality_group.addButton(radio)
            self._quality_layout.addWidget(radio)

    def _on_quality_changed(self, fmt: DownloadFormat, checked: bool):
        if checked:
            self.selected_format = fmt

    def _on_start(self):
        self.accept()

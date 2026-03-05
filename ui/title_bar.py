"""
✨ Eternal Media Downloader | Developed by Hearlov — Custom Title Bar
Frameless window title bar with minimize/close buttons
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QMouseEvent

from ui.theme import COLORS, DIMS, FONTS


class TitleBar(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._window = parent
        self._drag_pos = None
        self.setFixedHeight(DIMS["title_bar_height"])
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 8, 0)
        layout.setSpacing(0)
        self._title_label = QLabel("✦ Eternal Media Downloader")
        self._title_label.setFont(QFont(FONTS["primary"], 11, QFont.Weight.DemiBold))
        layout.addWidget(self._title_label)
        layout.addStretch()
        self._btn_minimize = self._create_control_btn("─", self._on_minimize)
        self._btn_close = self._create_control_btn("✕", self._on_close, is_close=True)
        layout.addWidget(self._btn_minimize)
        layout.addWidget(self._btn_close)

    def _create_control_btn(self, text: str, callback, is_close: bool = False) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedSize(36, 28)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(callback)

        hover_bg = COLORS["error"] if is_close else COLORS["bg_hover"]
        hover_color = "#FFFFFF" if is_close else COLORS["text_primary"]

        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS["text_secondary"]};
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {hover_bg};
                color: {hover_color};
            }}
        """)
        return btn

    def _apply_style(self):
        self.setStyleSheet(f"""
            TitleBar {{
                background: {COLORS["bg_secondary"]};
                border-top-left-radius: {DIMS["border_radius"]}px;
                border-top-right-radius: {DIMS["border_radius"]}px;
                border-bottom: 1px solid {COLORS["border"]};
            }}
        """)
        self._title_label.setStyleSheet(f"""
            color: {COLORS["text_secondary"]};
            background: transparent;
        """)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self._window.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._window.isMaximized():
                self._window.showNormal()
            else:
                self._window.showMaximized()

    def _on_minimize(self):
        self._window.showMinimized()

    def _on_close(self):
        self._window.close()

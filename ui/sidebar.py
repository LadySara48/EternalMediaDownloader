"""
✨ Eternal Media Downloader | Developed by Hearlov — Sidebar Navigation
Animated collapsible sidebar with icon + label navigation items
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize, pyqtProperty
)
from PyQt6.QtGui import QFont, QIcon

from ui.theme import COLORS, DIMS, FONTS

class SidebarItem(QPushButton):

    def __init__(self, icon_char: str, label: str, parent=None):
        super().__init__(parent)
        self._icon_char = icon_char
        self._label_text = label
        self._is_active = False
        self._is_expanded = False
        self._badge_count = 0
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(44)
        self.setMinimumWidth(DIMS["sidebar_collapsed"])
        self._update_display()

    def set_expanded(self, expanded: bool):
        self._is_expanded = expanded
        self._update_display()

    def set_active(self, active: bool):
        self._is_active = active
        self._update_style()

    def set_badge(self, count: int):
        self._badge_count = count
        self._update_display()

    def _update_display(self):
        badge = f" ({self._badge_count})" if self._badge_count > 0 else ""
        if self._is_expanded:
            self.setText(f"  {self._icon_char}    {self._label_text}{badge}")
        else:
            self.setText(f"{self._icon_char}{f' {self._badge_count}' if self._badge_count > 0 else ''}")
        self.setStyleSheet(self._get_style())

    def _update_style(self):
        self.setStyleSheet(self._get_style())

    def _get_style(self) -> str:
        bg = COLORS["accent_light"] if self._is_active else "transparent"
        text_color = COLORS["accent"] if self._is_active else COLORS["text_secondary"]
        left_border = f"3px solid {COLORS['accent']}" if self._is_active else "3px solid transparent"
        align = "left" if self._is_expanded else "center"
        font_size = "13px" if self._is_expanded else "18px"
        padding = "0 12px" if self._is_expanded else "0"

        return f"""
            QPushButton {{
                background: {bg};
                color: {text_color};
                border: none;
                border-left: {left_border};
                border-radius: 0px;
                font-size: {font_size};
                font-family: '{FONTS["primary"]}';
                font-weight: {'600' if self._is_active else 'normal'};
                text-align: {align};
                padding: {padding};
            }}
            QPushButton:hover {{
                background: {COLORS["bg_hover"]};
                color: {COLORS["text_primary"]};
            }}
        """

class Sidebar(QWidget):

    navigation_changed = pyqtSignal(str)

    SECTIONS = [
        ("⬇", "Downloading"),
        ("✓", "Completed"),
        ("◷", "History"),
        ("⚙", "Settings"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_expanded = False
        self._labels_visible = False
        self._items: list[SidebarItem] = []
        self._active_section = "Downloading"
        self.setFixedWidth(DIMS["sidebar_collapsed"])
        self._setup_ui()
        self._apply_style()
        self._setup_animation()
        self._items[0].set_active(True)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 12)
        layout.setSpacing(2)
        self._toggle_btn = QPushButton("☰")
        self._toggle_btn.setFixedSize(DIMS["sidebar_collapsed"], 40)
        self._toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_btn.clicked.connect(self.toggle)
        self._toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS["text_secondary"]};
                border: none;
                font-size: 18px;
            }}
            QPushButton:hover {{
                color: {COLORS["accent"]};
            }}
        """)
        layout.addWidget(self._toggle_btn)
        layout.addSpacing(12)
        for icon, label in self.SECTIONS:
            item = SidebarItem(icon, label)
            item.clicked.connect(lambda checked, lbl=label: self._on_item_clicked(lbl))
            self._items.append(item)
            layout.addWidget(item)
        layout.addStretch()
        self._version_label = QLabel("v1.0")
        self._version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._version_label.setStyleSheet(f"""
            color: {COLORS["text_muted"]};
            font-size: 10px;
            background: transparent;
        """)
        layout.addWidget(self._version_label)

    def _apply_style(self):
        self.setStyleSheet(f"""
            Sidebar {{
                background: {COLORS["bg_secondary"]};
                border-right: 1px solid {COLORS["border"]};
            }}
        """)

    def _setup_animation(self):
        self._anim = QPropertyAnimation(self, b"sidebarWidth")
        self._anim.setDuration(280)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._anim.valueChanged.connect(self._on_anim_value_changed)
        self._anim.finished.connect(self._on_anim_finished)

    def _get_sidebar_width(self):
        return self.minimumWidth()

    def _set_sidebar_width(self, w):
        self.setFixedWidth(int(w))

    sidebarWidth = pyqtProperty(int, _get_sidebar_width, _set_sidebar_width)

    def _on_anim_value_changed(self, value):
        threshold = (DIMS["sidebar_collapsed"] + DIMS["sidebar_expanded"]) // 2
        show_labels = int(value) > threshold
        if show_labels != self._labels_visible:
            self._labels_visible = show_labels
            for item in self._items:
                item.set_expanded(show_labels)
            self._version_label.setText("v1.0 — Hearlov" if show_labels else "v1.0")

    def _on_anim_finished(self):
        for item in self._items:
            item.set_expanded(self._is_expanded)
        self._version_label.setText(
            "v1.0 — Hearlov" if self._is_expanded else "v1.0"
        )

    def toggle(self):
        self._is_expanded = not self._is_expanded
        target = DIMS["sidebar_expanded"] if self._is_expanded else DIMS["sidebar_collapsed"]
        self._anim.stop()
        self._anim.setStartValue(self.width())
        self._anim.setEndValue(target)
        self._anim.start()
        self._toggle_btn.setText("✕" if self._is_expanded else "☰")

    def _on_item_clicked(self, section: str):
        if section == self._active_section:
            return
        self._active_section = section
        for item in self._items:
            item.set_active(item._label_text == section)
        self.navigation_changed.emit(section)

    def get_active_section(self) -> str:
        return self._active_section

    def set_section_badge(self, section: str, count: int):
        for item in self._items:
            if item._label_text == section:
                item.set_badge(count)
                break

"""
✨ Eternal Media Downloader | Developed by Hearlov — Main Window
Frameless modern window with custom title bar, sidebar, and content area
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize, QRectF
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QRegion

from ui.theme import COLORS, DIMS, GLOBAL_STYLE
from ui.title_bar import TitleBar
from ui.sidebar import Sidebar
from ui.pages import ContentStack


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Eternal Media Downloader")
        self.setMinimumSize(QSize(900, 600))
        self.resize(1060, 680)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Window
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(GLOBAL_STYLE)
        self._setup_ui()
        self._connect_signals()
        self._center_on_screen()

    def _setup_ui(self):
        self._container = QWidget()
        self._container.setObjectName("MainContainer")
        self._container.setStyleSheet(f"""
            #MainContainer {{
                background: {COLORS["bg_primary"]};
                border-radius: {DIMS["border_radius"]}px;
                border: 1px solid {COLORS["border"]};
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 100))
        self._container.setGraphicsEffect(shadow)
        main_layout = QVBoxLayout(self._container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self._title_bar = TitleBar(self)
        main_layout.addWidget(self._title_bar)
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        self._sidebar = Sidebar()
        self._content = ContentStack()
        body_layout.addWidget(self._sidebar)
        body_layout.addWidget(self._content, 1)
        main_layout.addWidget(body, 1)
        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(12, 12, 12, 12)
        wrapper_layout.addWidget(self._container)
        self.setCentralWidget(wrapper)

    def _connect_signals(self):
        self._sidebar.navigation_changed.connect(self._content.switch_to)
        dp = self._content.downloading_page
        dp.active_count_changed.connect(
            lambda count: self._sidebar.set_section_badge("Downloading", count)
        )

    def closeEvent(self, event):
        dp = self._content.downloading_page
        for task_id, task in dp._tasks.items():
            if task.is_running():
                task.cancel()
        event.accept()

    def _center_on_screen(self):
        screen = self.screen()
        if screen:
            geo = screen.availableGeometry()
            x = (geo.width() - self.width()) // 2
            y = (geo.height() - self.height()) // 2
            self.move(x, y)

    _RESIZE_MARGIN = 8

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            if self._is_resize_area(pos):
                self._resize_drag = True
                self._resize_origin = event.globalPosition().toPoint()
                self._resize_size = self.size()
                event.accept()
                return
        self._resize_drag = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if getattr(self, '_resize_drag', False) and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._resize_origin
            new_w = max(self.minimumWidth(), self._resize_size.width() + delta.x())
            new_h = max(self.minimumHeight(), self._resize_size.height() + delta.y())
            self.resize(new_w, new_h)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._resize_drag = False
        super().mouseReleaseEvent(event)

    def _is_resize_area(self, pos) -> bool:
        return (
            pos.x() > self.width() - self._RESIZE_MARGIN and
            pos.y() > self.height() - self._RESIZE_MARGIN
        )

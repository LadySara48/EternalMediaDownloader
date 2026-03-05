"""
Eternal Media Downloader | Developed by Hearlov
Modern Media Downloader for Windows
Python + PyQt6 Based UI Wrapper

Developer : Hearlov
GitHub    : https://github.com/LadySara48
License   : MIT

Since my Python knowledge is limited,
I used the Claude Opus 4.6 tool for support in some areas.

(Since I'm not very good at image generation,
I usually handled coding tasks like downloading and creating,
while I used Claude for support in the image generation part)
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.main_window import MainWindow


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Eternal Media Downloader")
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

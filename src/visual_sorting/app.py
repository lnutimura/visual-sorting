"""Application entry point and main window."""

from __future__ import annotations

import sys

import pyqtgraph as pg
from PySide6 import QtCore, QtGui, QtWidgets

from visual_sorting import __version__
from visual_sorting.sound import ToneEngine
from visual_sorting.views import MODES
from visual_sorting.widgets.race import RaceTab
from visual_sorting.widgets.single import SingleTab
from visual_sorting.widgets.tab import SortTab

STYLESHEET = """
QWidget { background: #161a22; color: #c9d1d9; font-size: 10pt; }
QGroupBox { border: 1px solid #2a3140; border-radius: 6px; margin-top: 14px; padding: 8px 6px 6px 6px; }
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; color: #8b949e; font-weight: bold; }
QPushButton { background: #222936; border: 1px solid #2f3747; border-radius: 4px; padding: 5px 10px; }
QPushButton:hover { background: #2b3444; }
QPushButton:pressed, QPushButton:checked { background: #3a4a66; border-color: #4f6591; }
QPushButton#primary { background: #2f6feb; border-color: #2f6feb; color: white; font-weight: bold; }
QPushButton#primary:hover { background: #4381f0; }
QPushButton#segment { border-radius: 0; }
QComboBox, QListWidget { background: #1c212b; border: 1px solid #2f3747; border-radius: 4px; padding: 3px; }
QComboBox QAbstractItemView { background: #1c212b; selection-background-color: #3a4a66; }
QListWidget::item { padding: 2px; }
QTabWidget::pane { border: none; }
QTabBar::tab { background: #1c212b; padding: 6px 18px; border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px; }
QTabBar::tab:selected { background: #2f6feb; color: white; }
QLabel#description, QLabel#hint { color: #8b949e; }
QLabel#complexity { color: #58a6ff; }
QLabel#status { font-weight: bold; color: #3ddc84; }
QLabel#stat { font-family: monospace; }
QCheckBox:disabled { color: #555d6b; }
"""


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"Visual Sorting {__version__}")
        self.resize(1280, 760)

        self.sound = ToneEngine(self)
        self.tabs = QtWidgets.QTabWidget()
        self.single = SingleTab(self.sound)
        self.race = RaceTab(self.sound)
        self.tabs.addTab(self.single, "Single")
        self.tabs.addTab(self.race, "Race")
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.setCentralWidget(self.tabs)
        for tab in self._all_tabs():
            tab.sound_toggled.connect(self.set_sound)

        shortcuts = {
            "Space": lambda: self.current.player.toggle(),
            ".": lambda: self.current.player.step(),
            "R": lambda: self.current.player.reset(),
            "S": lambda: self.current.new_input(),
            "M": lambda: self.set_sound(not self.sound.enabled),
        }
        for i, mode in enumerate(MODES, start=1):
            shortcuts[str(i)] = lambda mode=mode: self.current.set_mode(mode)
        for key, action in shortcuts.items():
            QtGui.QShortcut(QtGui.QKeySequence(key), self, activated=action)

    @property
    def current(self) -> SortTab:
        return self.tabs.currentWidget()

    def _all_tabs(self) -> list[SortTab]:
        return [self.single, self.race]

    def _on_tab_changed(self) -> None:
        for tab in self._all_tabs():
            if tab is not self.current:
                tab.player.pause()

    def set_sound(self, enabled: bool) -> None:
        self.sound.set_enabled(enabled)
        for tab in self._all_tabs():
            tab.panel.set_sound_checked(self.sound.enabled)


def main() -> None:
    QtWidgets.QApplication.setApplicationName("Visual Sorting")
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)
    pg.setConfigOptions(antialias=True)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

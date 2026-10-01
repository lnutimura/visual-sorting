"""Sidebar with input, playback and display controls, shared by both tabs."""

from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from visual_sorting.distributions import DISTRIBUTIONS
from visual_sorting.player import Stats
from visual_sorting.views import MODES

MIN_SIZE, MAX_SIZE, DEFAULT_SIZE = 8, 2000, 150
MIN_SPEED, MAX_SPEED = 2.0, 200_000.0
DEFAULT_SPEED_POS = 55
PANEL_WIDTH = 300


def speed_from_slider(pos: int) -> float:
    return MIN_SPEED * (MAX_SPEED / MIN_SPEED) ** (pos / 100)


def format_rate(value: float) -> str:
    if value >= 1000:
        return f"{value / 1000:.1f}k ops/s"
    return f"{value:.0f} ops/s"


class ControlPanel(QtWidgets.QWidget):
    input_changed = QtCore.Signal()
    speed_changed = QtCore.Signal(float)
    mode_changed = QtCore.Signal(str)
    sound_toggled = QtCore.Signal(bool)
    play_clicked = QtCore.Signal()
    step_clicked = QtCore.Signal()
    reset_clicked = QtCore.Signal()
    shuffle_clicked = QtCore.Signal()

    def __init__(self, algorithm_box: QtWidgets.QWidget, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(PANEL_WIDTH)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(algorithm_box)
        layout.addWidget(self._build_input())
        layout.addWidget(self._build_playback())
        layout.addWidget(self._build_display())
        self._extra = QtWidgets.QVBoxLayout()
        layout.addLayout(self._extra)
        layout.addStretch()
        hint = QtWidgets.QLabel(
            "<b>Space</b> play/pause &nbsp; <b>.</b> step &nbsp; <b>R</b> reset<br>"
            "<b>S</b> shuffle &nbsp; <b>M</b> sound &nbsp; <b>1/2/3</b> view"
        )
        hint.setObjectName("hint")
        layout.addWidget(hint)

    def _build_input(self) -> QtWidgets.QGroupBox:
        box = QtWidgets.QGroupBox("Input")
        form = QtWidgets.QFormLayout(box)
        self._distribution = QtWidgets.QComboBox()
        self._distribution.addItems(list(DISTRIBUTIONS))
        self._distribution.currentIndexChanged.connect(self.input_changed)
        form.addRow("Shape", self._distribution)

        self._size = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self._size.setRange(MIN_SIZE, MAX_SIZE)
        self._size.setValue(DEFAULT_SIZE)
        self._size_label = QtWidgets.QLabel(str(DEFAULT_SIZE))
        self._size_label.setMinimumWidth(36)
        self._size.valueChanged.connect(lambda v: self._size_label.setText(str(v)))
        self._size.valueChanged.connect(self.input_changed)
        row = QtWidgets.QHBoxLayout()
        row.addWidget(self._size)
        row.addWidget(self._size_label)
        form.addRow("Size", row)

        shuffle = self._button("Shuffle", self.shuffle_clicked)
        form.addRow(shuffle)
        return box

    def _build_playback(self) -> QtWidgets.QGroupBox:
        box = QtWidgets.QGroupBox("Playback")
        layout = QtWidgets.QVBoxLayout(box)
        self._speed = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self._speed.setRange(0, 100)
        self._speed.setValue(DEFAULT_SPEED_POS)
        self._speed_label = QtWidgets.QLabel()
        self._speed_label.setMinimumWidth(80)
        self._speed.valueChanged.connect(self._on_speed)
        row = QtWidgets.QHBoxLayout()
        row.addWidget(QtWidgets.QLabel("Speed"))
        row.addWidget(self._speed)
        row.addWidget(self._speed_label)
        layout.addLayout(row)
        self._on_speed(self._speed.value())

        buttons = QtWidgets.QHBoxLayout()
        self._play = self._button("Play", self.play_clicked)
        self._play.setObjectName("primary")
        buttons.addWidget(self._play, 2)
        buttons.addWidget(self._button("Step", self.step_clicked), 1)
        buttons.addWidget(self._button("Reset", self.reset_clicked), 1)
        layout.addLayout(buttons)
        return box

    def _build_display(self) -> QtWidgets.QGroupBox:
        box = QtWidgets.QGroupBox("Display")
        layout = QtWidgets.QVBoxLayout(box)
        modes = QtWidgets.QHBoxLayout()
        modes.setSpacing(0)
        self._modes = QtWidgets.QButtonGroup(self)
        for i, mode in enumerate(MODES):
            button = QtWidgets.QPushButton(mode)
            button.setCheckable(True)
            button.setChecked(i == 0)
            button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            button.setObjectName("segment")
            self._modes.addButton(button, i)
            modes.addWidget(button)
        self._modes.idClicked.connect(lambda i: self.mode_changed.emit(MODES[i]))
        layout.addLayout(modes)

        self._sound = QtWidgets.QCheckBox("Sound")
        self._sound.toggled.connect(self.sound_toggled)
        layout.addWidget(self._sound)
        return box

    def _button(self, text: str, signal: QtCore.SignalInstance) -> QtWidgets.QPushButton:
        button = QtWidgets.QPushButton(text)
        button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        button.clicked.connect(signal)
        return button

    def _on_speed(self, pos: int) -> None:
        rate = speed_from_slider(pos)
        self._speed_label.setText(format_rate(rate))
        self.speed_changed.emit(rate)

    def add_section(self, widget: QtWidgets.QWidget) -> None:
        self._extra.addWidget(widget)

    @property
    def distribution(self) -> str:
        return self._distribution.currentText()

    @property
    def size(self) -> int:
        return self._size.value()

    @property
    def events_per_second(self) -> float:
        return speed_from_slider(self._speed.value())

    def set_playing(self, playing: bool) -> None:
        self._play.setText("Pause" if playing else "Play")

    def set_mode(self, mode: str) -> None:
        self._modes.button(MODES.index(mode)).setChecked(True)

    def set_sound_available(self, available: bool) -> None:
        self._sound.setEnabled(available)
        if not available:
            self._sound.setToolTip("No audio output device found")

    def set_sound_checked(self, checked: bool) -> None:
        with QtCore.QSignalBlocker(self._sound):
            self._sound.setChecked(checked)


class StatsBox(QtWidgets.QGroupBox):
    """Live counters for a single run."""

    FIELDS = (("Comparisons", "comparisons"), ("Swaps", "swaps"), ("Writes", "writes"), ("Steps", "steps"))

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__("Statistics", parent)
        grid = QtWidgets.QGridLayout(self)
        self._status = QtWidgets.QLabel()
        self._status.setObjectName("status")
        grid.addWidget(self._status, 0, 0, 1, 2)
        self._values: dict[str, QtWidgets.QLabel] = {}
        for row, (label, attr) in enumerate(self.FIELDS, start=1):
            grid.addWidget(QtWidgets.QLabel(label), row, 0)
            value = QtWidgets.QLabel("0")
            value.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
            value.setObjectName("stat")
            grid.addWidget(value, row, 1)
            self._values[attr] = value

    def show_stats(self, stats: Stats, status: str) -> None:
        self._status.setText(status)
        for attr, label in self._values.items():
            label.setText(f"{getattr(stats, attr):,}")

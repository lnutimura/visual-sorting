"""Behaviour shared by the Single and Race tabs."""

from __future__ import annotations

import random

from PySide6 import QtCore, QtWidgets

from visual_sorting.distributions import DISTRIBUTIONS
from visual_sorting.player import Player
from visual_sorting.sound import ToneEngine
from visual_sorting.views import MODES, SortView
from visual_sorting.widgets.control_panel import ControlPanel


class SortTab(QtWidgets.QWidget):
    """A control panel, a player and one or more views on a common input."""

    sound_toggled = QtCore.Signal(bool)

    def __init__(self, sound: ToneEngine, algorithm_box: QtWidgets.QWidget, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.sound = sound
        self.mode = MODES[0]
        self.values: list[int] = []
        self._rng = random.Random()

        self.panel = ControlPanel(algorithm_box)
        self.player = Player(self)
        self.player.events_per_second = self.panel.events_per_second

        self.panel.input_changed.connect(self.new_input)
        self.panel.shuffle_clicked.connect(self.new_input)
        self.panel.speed_changed.connect(lambda rate: setattr(self.player, "events_per_second", rate))
        self.panel.mode_changed.connect(self.set_mode)
        self.panel.sound_toggled.connect(self.sound_toggled)
        self.panel.play_clicked.connect(self.player.toggle)
        self.panel.step_clicked.connect(self.player.step)
        self.panel.reset_clicked.connect(self.player.reset)
        self.panel.set_sound_available(sound.available)
        self.player.playing_changed.connect(self.panel.set_playing)
        self.player.playing_changed.connect(self.refresh)
        self.player.ticked.connect(self.refresh)

    def views(self) -> list[SortView]:
        raise NotImplementedError

    def rebuild(self) -> None:
        """Recreate runs (and reload views) for ``self.values``."""
        raise NotImplementedError

    def refresh(self) -> None:
        """Push the current run state to the views."""
        raise NotImplementedError

    def new_input(self) -> None:
        self.values = DISTRIBUTIONS[self.panel.distribution](self.panel.size, self._rng)
        self.rebuild()

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        self.panel.set_mode(mode)
        for view in self.views():
            view.set_mode(mode)

    def play_notes(self) -> None:
        vmax = max(self.values, default=1)
        self.sound.set_notes([
            run.last_value / vmax
            for run in self.player.runs
            if not run.done and run.stats.steps and run.last_value is not None
        ])

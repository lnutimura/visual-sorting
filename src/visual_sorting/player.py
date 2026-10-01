"""Drives algorithm generators at a controllable speed."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from PySide6 import QtCore

from visual_sorting.algorithms import Algorithm
from visual_sorting.events import Compare, Swap, Write

TICK_MS = 16


@dataclass
class Stats:
    comparisons: int = 0
    swaps: int = 0
    writes: int = 0
    steps: int = 0


class SortRun:
    """One algorithm sorting one array, advanced a few events at a time."""

    def __init__(self, algorithm: Algorithm, values: Sequence[int]) -> None:
        self.algorithm = algorithm
        self.initial = list(values)
        self.reset()

    def reset(self) -> None:
        self.array = list(self.initial)
        self._events = self.algorithm.run(self.array)
        self.stats = Stats()
        self.done = False
        self.compared: tuple[int, ...] = ()
        self.written: tuple[int, ...] = ()
        self.last_value: int | None = None

    def advance(self, budget: int) -> int:
        """Process up to ``budget`` events; returns how many were processed."""
        arr, stats = self.array, self.stats
        compared: tuple[int, ...] = ()
        written: tuple[int, ...] = ()
        last_index = None
        processed = 0
        while processed < budget and not self.done:
            event = next(self._events, None)
            if event is None:
                self.done = True
                break
            processed += 1
            kind = type(event)
            if kind is Compare:
                stats.comparisons += 1
                compared = (event.i, event.j)
                last_index = event.j
            elif kind is Swap:
                arr[event.i], arr[event.j] = arr[event.j], arr[event.i]
                stats.swaps += 1
                stats.writes += 2
                written = (event.i, event.j)
                last_index = event.j
            elif kind is Write:
                arr[event.i] = event.value
                stats.writes += 1
                written = (event.i,)
                last_index = event.i
        stats.steps += processed
        self.compared = () if self.done else compared
        self.written = () if self.done else written
        if last_index is not None:
            self.last_value = arr[last_index]
        return processed


class Player(QtCore.QObject):
    """Advances a group of runs together from a single timer."""

    ticked = QtCore.Signal()
    run_finished = QtCore.Signal(int)
    finished = QtCore.Signal()
    playing_changed = QtCore.Signal(bool)

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self.runs: list[SortRun] = []
        self.events_per_second = 500.0
        self._carry = 0.0
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(TICK_MS)
        self._timer.timeout.connect(self._on_timeout)
        self._clock = QtCore.QElapsedTimer()

    @property
    def playing(self) -> bool:
        return self._timer.isActive()

    @property
    def all_done(self) -> bool:
        return all(run.done for run in self.runs)

    def set_runs(self, runs: list[SortRun]) -> None:
        self.pause()
        self.runs = runs
        self.ticked.emit()

    def play(self) -> None:
        if self.playing or not self.runs or self.all_done:
            return
        self._carry = 0.0
        self._clock.start()
        self._timer.start()
        self.playing_changed.emit(True)

    def pause(self) -> None:
        if self.playing:
            self._timer.stop()
            self.playing_changed.emit(False)

    def toggle(self) -> None:
        if self.playing:
            self.pause()
        elif self.all_done:
            self.reset()
            self.play()
        else:
            self.play()

    def step(self) -> None:
        self.pause()
        self._advance(1)

    def reset(self) -> None:
        self.pause()
        for run in self.runs:
            run.reset()
        self.ticked.emit()

    def _on_timeout(self) -> None:
        elapsed = self._clock.restart() / 1000.0
        # Clamp so a stalled event loop doesn't trigger a huge catch-up burst.
        self._carry += self.events_per_second * min(elapsed, 0.1)
        budget = int(self._carry)
        self._carry -= budget
        if budget:
            self._advance(budget)

    def _advance(self, budget: int) -> None:
        for index, run in enumerate(self.runs):
            if not run.done:
                run.advance(budget)
                if run.done:
                    self.run_finished.emit(index)
        self.ticked.emit()
        if self.all_done:
            self.pause()
            self.finished.emit()

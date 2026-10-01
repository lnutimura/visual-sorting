"""Several algorithms racing on identical copies of the same input."""

from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from visual_sorting.algorithms import ALGORITHMS
from visual_sorting.player import SortRun
from visual_sorting.sound import ToneEngine
from visual_sorting.views import SortView
from visual_sorting.widgets.tab import SortTab

MAX_RACERS = 6
DEFAULT_RACERS = ("insertion", "shell", "heap", "quick_middle")
MEDALS = ("1st", "2nd", "3rd", "4th", "5th", "6th")


class RaceTab(SortTab):
    def __init__(self, sound: ToneEngine, parent: QtWidgets.QWidget | None = None) -> None:
        box = QtWidgets.QGroupBox(f"Contestants (up to {MAX_RACERS})")
        layout = QtWidgets.QVBoxLayout(box)
        picker = QtWidgets.QListWidget()
        for algo in ALGORITHMS.values():
            item = QtWidgets.QListWidgetItem(algo.name)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, algo.key)
            item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            checked = algo.key in DEFAULT_RACERS
            item.setCheckState(QtCore.Qt.CheckState.Checked if checked else QtCore.Qt.CheckState.Unchecked)
            picker.addItem(item)
        picker.setMinimumHeight(220)
        results = QtWidgets.QLabel()
        results.setWordWrap(True)
        results.setObjectName("description")
        layout.addWidget(picker)
        layout.addWidget(results)

        super().__init__(sound, box, parent)
        self._picker = picker
        self._results = results
        self._finish_order: list[int] = []
        self._views = [SortView() for _ in range(MAX_RACERS)]
        self._grid = QtWidgets.QGridLayout()
        self._grid.setSpacing(6)

        root = QtWidgets.QHBoxLayout(self)
        root.addWidget(self.panel)
        root.addLayout(self._grid, 1)

        picker.itemChanged.connect(self._on_item_changed)
        self.player.run_finished.connect(self._finish_order.append)
        self.new_input()

    def _selected(self) -> list[str]:
        return [
            item.data(QtCore.Qt.ItemDataRole.UserRole)
            for item in (self._picker.item(i) for i in range(self._picker.count()))
            if item.checkState() == QtCore.Qt.CheckState.Checked
        ]

    def _on_item_changed(self, item: QtWidgets.QListWidgetItem) -> None:
        count = len(self._selected())
        if count > MAX_RACERS or count == 0:
            with QtCore.QSignalBlocker(self._picker):
                item.setCheckState(
                    QtCore.Qt.CheckState.Unchecked if count > MAX_RACERS else QtCore.Qt.CheckState.Checked
                )
            return
        self.rebuild()

    def views(self) -> list[SortView]:
        return self._views

    def rebuild(self) -> None:
        keys = self._selected()
        cols = 1 if len(keys) == 1 else 2 if len(keys) <= 4 else 3
        for view in self._views:
            self._grid.removeWidget(view)
            view.hide()
        for i, key in enumerate(keys):
            view = self._views[i]
            view.load(self.values)
            self._grid.addWidget(view, i // cols, i % cols)
            view.show()
        self._finish_order.clear()
        self.player.set_runs([SortRun(ALGORITHMS[key], self.values) for key in keys])

    def refresh(self) -> None:
        runs = self.player.runs
        # Runs that were reset are no longer finished.
        self._finish_order[:] = [i for i in self._finish_order if runs[i].done]
        for i, (run, view) in enumerate(zip(runs, self._views)):
            view.show_state(run.array, run.compared, run.written, run.done)
            medal = f"<b>{MEDALS[self._finish_order.index(i)]}</b> &nbsp;" if run.done else ""
            stats = run.stats
            view.set_caption(
                f"{medal}{run.algorithm.name} &nbsp;·&nbsp; {stats.comparisons:,} cmp &nbsp;·&nbsp; {stats.writes:,} writes"
            )
        if self._finish_order:
            names = [f"{n}. {runs[i].algorithm.name}" for n, i in enumerate(self._finish_order, start=1)]
            self._results.setText("Finish order (by operations):<br>" + "<br>".join(names))
        else:
            self._results.setText("Every contestant gets the same number of operations per frame.")
        self.play_notes()

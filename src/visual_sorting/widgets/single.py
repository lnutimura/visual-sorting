"""One algorithm, one big view, live statistics."""

from __future__ import annotations

from PySide6 import QtWidgets

from visual_sorting.algorithms import ALGORITHMS, Algorithm
from visual_sorting.player import SortRun
from visual_sorting.sound import ToneEngine
from visual_sorting.views import SortView
from visual_sorting.widgets.control_panel import StatsBox
from visual_sorting.widgets.tab import SortTab

DEFAULT_ALGORITHM = "quick_middle"


class SingleTab(SortTab):
    def __init__(self, sound: ToneEngine, parent: QtWidgets.QWidget | None = None) -> None:
        box = QtWidgets.QGroupBox("Algorithm")
        layout = QtWidgets.QVBoxLayout(box)
        picker = QtWidgets.QComboBox()
        picker.setMaxVisibleItems(len(ALGORITHMS) + 8)
        family = None
        for algo in ALGORITHMS.values():
            if family is not None and algo.family != family:
                picker.insertSeparator(picker.count())
            family = algo.family
            picker.addItem(algo.name, algo.key)
        picker.setCurrentIndex(picker.findData(DEFAULT_ALGORITHM))
        complexity = QtWidgets.QLabel()
        complexity.setObjectName("complexity")
        description = QtWidgets.QLabel()
        description.setWordWrap(True)
        description.setObjectName("description")
        layout.addWidget(picker)
        layout.addWidget(complexity)
        layout.addWidget(description)

        super().__init__(sound, box, parent)
        self._picker = picker
        self._complexity = complexity
        self._description = description
        self.view = SortView()
        self.stats = StatsBox()
        self.panel.add_section(self.stats)

        root = QtWidgets.QHBoxLayout(self)
        root.addWidget(self.panel)
        root.addWidget(self.view, 1)

        self._picker.currentIndexChanged.connect(self._on_algorithm)
        self._on_algorithm()

    @property
    def algorithm(self) -> Algorithm:
        return ALGORITHMS[self._picker.currentData()]

    def views(self) -> list[SortView]:
        return [self.view]

    def _on_algorithm(self) -> None:
        algo = self.algorithm
        self._complexity.setText(f"{algo.family} · average {algo.complexity}")
        self._description.setText(algo.description)
        self.view.set_caption(algo.name)
        if self.values:
            self.rebuild()
        else:
            self.new_input()

    def rebuild(self) -> None:
        self.view.load(self.values)
        self.player.set_runs([SortRun(self.algorithm, self.values)])

    def refresh(self) -> None:
        if not self.player.runs:
            return
        run = self.player.runs[0]
        self.view.show_state(run.array, run.compared, run.written, run.done)
        if run.done:
            status = "Sorted"
        elif self.player.playing:
            status = "Running"
        else:
            status = "Paused" if run.stats.steps else "Ready"
        self.stats.show_stats(run.stats, status)
        self.play_notes()

"""Render the README animations and screenshot into ``docs/``.

Runs headless:  QT_QPA_PLATFORM=offscreen python scripts/record_gifs.py
"""

from __future__ import annotations

import math
import random
from pathlib import Path

import pyqtgraph as pg
from PIL import Image
from PySide6 import QtCore, QtGui, QtWidgets

from visual_sorting.algorithms import ALGORITHMS
from visual_sorting.app import STYLESHEET, MainWindow
from visual_sorting.distributions import DISTRIBUTIONS
from visual_sorting.player import SortRun
from visual_sorting.views import SWEEP_MS, SWEEP_TICK_MS, SortView

DOCS = Path(__file__).resolve().parent.parent / "docs"
FRAMES = 90
FRAME_MS = 40
HOLD_FRAMES = 25

CLIPS = [
    # file, algorithms, distribution, size, mode, (width, height)
    ("quick_dots", ["quick_middle"], "Random", 200, "Dots", (480, 300)),
    ("heap_spiral", ["heap"], "Random", 300, "Spiral", (360, 360)),
    ("merge_bars", ["merge"], "Random", 160, "Bars", (480, 300)),
    ("radix_dots", ["radix"], "Random", 300, "Dots", (480, 300)),
    ("race", ["insertion", "shell", "heap", "quick_middle"], "Random", 150, "Dots", (720, 440)),
]


def wait(ms: int) -> None:
    loop = QtCore.QEventLoop()
    QtCore.QTimer.singleShot(ms, loop.quit)
    loop.exec()


def to_pil(widget: QtWidgets.QWidget) -> Image.Image:
    image = widget.grab().toImage().convertToFormat(QtGui.QImage.Format.Format_RGB888)
    return Image.frombuffer(
        "RGB", (image.width(), image.height()), bytes(image.constBits()), "raw", "RGB", image.bytesPerLine(), 1
    ).copy()


def total_events(key: str, values: list[int]) -> int:
    run = SortRun(ALGORITHMS[key], values)
    while not run.done:
        run.advance(1_000_000)
    return run.stats.steps


def record(name: str, keys: list[str], distribution: str, size: int, mode: str, dims: tuple[int, int]) -> None:
    values = DISTRIBUTIONS[distribution](size, random.Random(7))
    budget = max(1, math.ceil(max(total_events(k, values) for k in keys) / FRAMES))
    runs = [SortRun(ALGORITHMS[k], values) for k in keys]

    container = QtWidgets.QWidget()
    container.setStyleSheet("background: #101218;")
    grid = QtWidgets.QGridLayout(container)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setSpacing(4)
    views = []
    for i, run in enumerate(runs):
        view = SortView()
        view.load(values)
        view.set_mode(mode)
        view.set_caption(run.algorithm.name)
        grid.addWidget(view, i // 2, i % 2)
        views.append(view)
    container.resize(*dims)
    container.show()

    frames = []
    while True:
        for run, view in zip(runs, views):
            run.advance(budget)
            view.show_state(run.array, run.compared, run.written, run.done)
        QtWidgets.QApplication.processEvents()
        frames.append(to_pil(container))
        if all(run.done for run in runs):
            break
    for _ in range(math.ceil(SWEEP_MS / SWEEP_TICK_MS / 2)):
        wait(SWEEP_TICK_MS * 2)
        frames.append(to_pil(container))
    frames.extend([frames[-1]] * HOLD_FRAMES)

    palette = [f.convert("P", palette=Image.Palette.ADAPTIVE, colors=96) for f in frames]
    path = DOCS / f"{name}.gif"
    palette[0].save(path, save_all=True, append_images=palette[1:], duration=FRAME_MS, loop=0, optimize=True)
    print(f"wrote {path.relative_to(DOCS.parent)} ({len(frames)} frames, {path.stat().st_size // 1024} KiB)")
    container.close()


def screenshot() -> None:
    window = MainWindow()
    window.resize(1280, 720)
    window.show()
    tab = window.single
    tab.set_mode("Dots")
    tab.player.events_per_second = 700
    tab.player.play()
    wait(1400)
    tab.player.pause()
    path = DOCS / "screenshot.png"
    window.grab().save(str(path))
    print(f"wrote {path.relative_to(DOCS.parent)}")
    window.close()


def main() -> None:
    app = QtWidgets.QApplication([])
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)
    pg.setConfigOptions(antialias=True)
    DOCS.mkdir(exist_ok=True)
    for clip in CLIPS:
        record(*clip)
    screenshot()


if __name__ == "__main__":
    main()

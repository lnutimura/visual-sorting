"""Plot widget that renders an array as dots, bars, or a colour spiral."""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np
import pyqtgraph as pg
from PySide6 import QtCore, QtGui

BACKGROUND = "#101218"
COMPARE_COLOR = "#ffffff"
WRITE_COLOR = "#ff3b3b"
DONE_COLOR = "#3ddc84"
SWEEP_MS = 900
SWEEP_TICK_MS = 16
SWEEP_HOLD_MS = 400
BAR_ROWS = 400
BAR_TARGET_WIDTH_PX = 800

MODES = ("Dots", "Bars", "Spiral")


def _rgba(color: str) -> np.ndarray:
    c = QtGui.QColor(color)
    return np.array([c.red(), c.green(), c.blue(), 255], dtype=np.uint8)


class SortView(pg.PlotWidget):
    """Draws one array. Colour encodes value, so the eye can follow where
    each element travels; the layout (``mode``) is interchangeable."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent, background=BACKGROUND)
        self.setMenuEnabled(False)
        self.setMouseEnabled(False, False)
        self.hideButtons()
        self.hideAxis("left")
        self.hideAxis("bottom")
        self.setAntialiasing(True)

        self._mode = MODES[0]
        self._array: Sequence[int] = []
        self._compared: tuple[int, ...] = ()
        self._written: tuple[int, ...] = ()
        self._done = False
        self._sweep = 0

        # Bars are rasterised with numpy into one image: far faster than a
        # BarGraphItem with per-bar brushes once n reaches the thousands.
        self._image = pg.ImageItem(axisOrder="row-major")
        self._points = pg.ScatterPlotItem(pen=None, pxMode=True)
        self._hl_compare = pg.ScatterPlotItem(pen=pg.mkPen(COMPARE_COLOR, width=2), brush=None, pxMode=True)
        self._hl_write = pg.ScatterPlotItem(pen=None, brush=pg.mkBrush(WRITE_COLOR), pxMode=True)
        for item in (self._image, self._points, self._hl_compare, self._hl_write):
            self.addItem(item)

        self._done_brush = pg.mkBrush(DONE_COLOR)
        self._compare_rgba = _rgba(COMPARE_COLOR)
        self._write_rgba = _rgba(WRITE_COLOR)
        self._done_rgba = _rgba(DONE_COLOR)

        self._sweep_timer = QtCore.QTimer(self)
        self._sweep_timer.setInterval(SWEEP_TICK_MS)
        self._sweep_timer.timeout.connect(self._advance_sweep)

        self.load([])

    @property
    def mode(self) -> str:
        return self._mode

    def set_mode(self, mode: str) -> None:
        self._mode = mode
        self._apply_layout()
        self._render()

    def set_caption(self, text: str) -> None:
        self.setTitle(text, color="#c9d1d9", size="10pt")

    def load(self, values: Sequence[int]) -> None:
        """Prepare for a new input; ``values`` is the multiset being sorted."""
        self._sweep_timer.stop()
        self._array = list(values)
        self._compared = self._written = ()
        self._done = False
        self._sweep = 0

        n = len(values)
        self._n = n
        vmax = max(values, default=1)
        self._vmax = vmax
        ranked = sorted(values)
        # First/last index each value occupies once sorted, for the spiral.
        self._first = np.zeros(vmax + 1, dtype=np.int64)
        self._last = np.zeros(vmax + 1, dtype=np.int64)
        for idx, v in enumerate(ranked):
            if idx == 0 or ranked[idx - 1] != v:
                self._first[v] = idx
            self._last[v] = idx

        vmin = ranked[0] if ranked else 0
        span = max(1, vmax - vmin + 1)
        colors = [QtGui.QColor.fromHsvF(((v - vmin) / span) % 1.0, 0.72, 1.0) for v in range(vmax + 1)]
        self._brush_lut = [pg.mkBrush(c) for c in colors]
        self._rgba_lut = np.array([[c.red(), c.green(), c.blue(), 255] for c in colors], dtype=np.uint8)

        indices = np.arange(n)
        theta = math.pi / 2 - 2 * math.pi * indices / max(n, 1)
        self._cos, self._sin = np.cos(theta), np.sin(theta)

        self._bar_rows = min(BAR_ROWS, vmax)
        self._bar_px = max(1, BAR_TARGET_WIDTH_PX // max(n, 1))
        self._row_levels = (np.arange(self._bar_rows) + 0.5)[:, None] * (vmax / self._bar_rows)

        size = float(np.clip(1200 / max(n, 1), 3, 10))
        self._points.setSize(size)
        self._hl_compare.setSize(size + 6)
        self._hl_write.setSize(size + 3)
        self._apply_layout()
        self._render()

    def show_state(self, array: Sequence[int], compared: tuple[int, ...], written: tuple[int, ...], done: bool) -> None:
        self._array = array
        self._compared = compared
        self._written = written
        if done and not self._done:
            self._done = True
            self._sweep = 0
            self._sweep_timer.setInterval(SWEEP_TICK_MS)
            self._sweep_timer.start()
        elif not done:
            self._done = False
            self._sweep_timer.stop()
            self._sweep = 0
        self._render()

    def _apply_layout(self) -> None:
        bars = self._mode == "Bars"
        self._image.setVisible(bars)
        for item in (self._points, self._hl_compare, self._hl_write):
            item.setVisible(not bars)
        n, vmax = max(self._n, 1), max(self._vmax, 1)
        if self._mode == "Spiral":
            self.setAspectLocked(True)
            self.setRange(xRange=(-1.05, 1.05), yRange=(-1.05, 1.05), padding=0)
        else:
            self.setAspectLocked(False)
            self.setRange(xRange=(-1, n), yRange=(0, vmax * 1.02), padding=0.02)

    def _render(self) -> None:
        arr = np.asarray(self._array, dtype=np.int64)
        compared = np.asarray(self._compared, dtype=np.int64)
        written = np.asarray(self._written, dtype=np.int64)
        if self._mode == "Bars":
            self._render_bars(arr, compared, written)
            return

        lut = self._brush_lut
        brushes = [lut[v] for v in self._array]
        if self._sweep:
            brushes[: self._sweep] = [self._done_brush] * self._sweep
        idx = np.arange(len(arr))
        if self._mode == "Spiral":
            dist = np.maximum(self._first[arr] - idx, 0) + np.maximum(idx - self._last[arr], 0)
            r = 1.0 - 0.85 * dist / max(self._n, 1)
            x, y = r * self._cos, r * self._sin
        else:
            x, y = idx.astype(float), arr.astype(float)
        self._points.setData(x=x, y=y, brush=brushes)
        self._hl_compare.setData(x=x[compared], y=y[compared])
        self._hl_write.setData(x=x[written], y=y[written])

    def _render_bars(self, arr: np.ndarray, compared: np.ndarray, written: np.ndarray) -> None:
        if not len(arr):
            self._image.clear()
            return
        colors = self._rgba_lut[arr]
        colors[: self._sweep] = self._done_rgba
        colors[compared] = self._compare_rgba
        colors[written] = self._write_rgba
        filled = self._row_levels < arr[None, :]
        image = colors[None, :, :] * filled[..., None]
        px = self._bar_px
        if px > 1:
            image = np.repeat(image, px, axis=1)
            if px >= 3:
                image[:, px - 1 :: px] = 0
        self._image.setImage(image, autoLevels=False, levels=(0, 255),
                             rect=QtCore.QRectF(-0.5, 0, self._n, self._vmax))

    def _advance_sweep(self) -> None:
        if self._sweep >= self._n:
            self._sweep_timer.stop()
            self._sweep = 0
        else:
            step = max(1, math.ceil(self._n * SWEEP_TICK_MS / SWEEP_MS))
            self._sweep = min(self._n, self._sweep + step)
            if self._sweep >= self._n:
                self._sweep_timer.setInterval(SWEEP_HOLD_MS)
                self._sweep_timer.start()
        self._render()

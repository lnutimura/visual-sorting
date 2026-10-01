"""Optional audio: a small synthesiser that turns accessed values into pitch."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from PySide6 import QtCore
from PySide6.QtMultimedia import QAudioFormat, QAudioSink, QMediaDevices

SAMPLE_RATE = 44_100
BUFFER_MS = 80
NOTE_HOLD_MS = 60
MIN_HZ, MAX_HZ = 120.0, 1200.0
VOICE_GAIN = 0.22
MAX_VOICES = 6


def value_to_hz(fraction: float) -> float:
    """Map 0..1 onto an exponential (musical) pitch range."""
    return MIN_HZ * (MAX_HZ / MIN_HZ) ** min(max(fraction, 0.0), 1.0)


def triangle(phase: np.ndarray) -> np.ndarray:
    return 4.0 * np.abs(phase - np.floor(phase + 0.5)) - 1.0


class _ToneDevice(QtCore.QIODevice):
    """Read-only device the audio sink pulls freshly synthesised samples from."""

    def __init__(self, engine: ToneEngine) -> None:
        super().__init__(engine)
        self._engine = engine

    def isSequential(self) -> bool:
        return True

    def bytesAvailable(self) -> int:
        return SAMPLE_RATE * 2 + super().bytesAvailable()

    def readData(self, maxlen: int) -> bytes:
        return self._engine.render(maxlen // 2).tobytes()

    def writeData(self, data: bytes) -> int:
        return -1


class ToneEngine(QtCore.QObject):
    """Plays up to ``MAX_VOICES`` triangle tones, one per running sort.

    Disabled by default. If no audio output is available, ``available`` is
    False and ``set_enabled`` does nothing.
    """

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self.enabled = False
        self._sink: QAudioSink | None = None
        self._device = _ToneDevice(self)
        self._voices = 0
        self._freqs = np.zeros(MAX_VOICES)
        self._phases = np.zeros(MAX_VOICES)
        self._amps = np.zeros(MAX_VOICES)
        self._note_clock = QtCore.QElapsedTimer()

        device = QMediaDevices.defaultAudioOutput()
        fmt = QAudioFormat()
        fmt.setSampleRate(SAMPLE_RATE)
        fmt.setChannelCount(1)
        fmt.setSampleFormat(QAudioFormat.SampleFormat.Int16)
        if device.isNull() or not device.isFormatSupported(fmt):
            return
        self._sink = QAudioSink(device, fmt, self)
        self._sink.setBufferSize(SAMPLE_RATE * 2 * BUFFER_MS // 1000)

    @property
    def available(self) -> bool:
        return self._sink is not None

    def set_enabled(self, enabled: bool) -> None:
        if not self.available or enabled == self.enabled:
            return
        self.enabled = enabled
        if enabled:
            self._amps[:] = 0
            self._device.open(QtCore.QIODevice.OpenModeFlag.ReadOnly)
            self._sink.start(self._device)
        else:
            self._sink.stop()
            self._device.close()

    def set_notes(self, fractions: Sequence[float]) -> None:
        """Set the current pitches, each a value scaled to 0..1."""
        if not self.enabled:
            return
        fractions = fractions[:MAX_VOICES]
        self._voices = len(fractions)
        for v, f in enumerate(fractions):
            self._freqs[v] = value_to_hz(f)
        self._note_clock.start()

    def render(self, frames: int) -> np.ndarray:
        """Synthesise the next ``frames`` mono samples as int16."""
        holding = self._note_clock.isValid() and self._note_clock.elapsed() < NOTE_HOLD_MS
        out = np.zeros(frames)
        if frames <= 0:
            return out.astype(np.int16)
        t = np.arange(1, frames + 1) / SAMPLE_RATE
        ramp = np.linspace(0.0, 1.0, frames)
        for v in range(MAX_VOICES):
            target = VOICE_GAIN if holding and v < self._voices else 0.0
            if self._amps[v] == 0.0 and target == 0.0:
                continue
            phase = self._phases[v] + self._freqs[v] * t
            out += (self._amps[v] + (target - self._amps[v]) * ramp) * triangle(phase)
            self._phases[v] = phase[-1] % 1.0
            self._amps[v] = target
        out /= np.sqrt(max(1, self._voices))
        return (np.clip(out, -1.0, 1.0) * 32767).astype(np.int16)

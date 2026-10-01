import time

import numpy as np
import pytest
from PySide6 import QtCore

from visual_sorting.sound import NOTE_HOLD_MS, SAMPLE_RATE, ToneEngine, value_to_hz


@pytest.fixture(scope="module")
def qapp():
    return QtCore.QCoreApplication.instance() or QtCore.QCoreApplication([])


def dominant_hz(samples: np.ndarray) -> float:
    spectrum = np.abs(np.fft.rfft(samples))
    return (np.argmax(spectrum[1:]) + 1) * SAMPLE_RATE / len(samples)


def test_disabled_engine_ignores_notes(qapp):
    engine = ToneEngine()
    engine.set_notes([0.5])
    assert not np.any(engine.render(SAMPLE_RATE // 10))


def test_note_pitch_and_release(qapp):
    engine = ToneEngine()
    engine.enabled = True  # bypass the audio device; only synthesis is under test
    engine.set_notes([0.5])
    samples = engine.render(SAMPLE_RATE).astype(float)
    assert abs(dominant_hz(samples) - value_to_hz(0.5)) < 2

    time.sleep(NOTE_HOLD_MS / 1000 + 0.02)
    engine.render(256)  # fade-out chunk
    assert not np.any(engine.render(256))

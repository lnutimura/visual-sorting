import pytest
from PySide6 import QtCore

from visual_sorting.algorithms import ALGORITHMS
from visual_sorting.player import Player, SortRun


@pytest.fixture(scope="module")
def qapp():
    return QtCore.QCoreApplication.instance() or QtCore.QCoreApplication([])


def test_counters_for_bubble_sort_on_reversed_input():
    n = 10
    run = SortRun(ALGORITHMS["bubble"], list(range(n, 0, -1)))
    while not run.done:
        run.advance(7)
    pairs = n * (n - 1) // 2
    assert run.stats.comparisons == pairs
    assert run.stats.swaps == pairs
    assert run.stats.writes == 2 * pairs
    assert run.stats.steps == 2 * pairs


def test_advance_respects_budget_and_reports_highlights():
    run = SortRun(ALGORITHMS["bubble"], [2, 1, 3])
    assert run.advance(1) == 1
    assert run.compared == (0, 1)
    assert run.array == [2, 1, 3]
    run.advance(1)
    assert run.written == (0, 1)
    assert run.array == [1, 2, 3]


def test_reset_restores_input_and_counters():
    values = [5, 3, 4, 1, 2]
    run = SortRun(ALGORITHMS["heap"], values)
    run.advance(1000)
    assert run.done
    run.reset()
    assert run.array == values
    assert not run.done
    assert run.stats.steps == 0


def test_player_step_and_finish(qapp):
    player = Player()
    finished = []
    player.run_finished.connect(finished.append)
    player.set_runs([
        SortRun(ALGORITHMS["insertion"], [3, 2, 1]),
        SortRun(ALGORITHMS["merge"], [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]),
    ])
    player.step()
    assert not player.playing
    assert player.runs[0].stats.steps == 1
    while not player.all_done:
        player.step()
    assert finished == [0, 1]


def test_player_play_runs_to_completion(qapp):
    player = Player()
    player.events_per_second = 1_000_000
    player.set_runs([SortRun(ALGORITHMS["quick_middle"], list(range(200, 0, -1)))])
    loop = QtCore.QEventLoop()
    player.finished.connect(loop.quit)
    QtCore.QTimer.singleShot(5000, loop.quit)
    player.play()
    assert player.playing
    loop.exec()
    assert player.all_done and not player.playing
    assert player.runs[0].array == list(range(1, 201))


def test_toggle_after_finish_restarts(qapp):
    player = Player()
    player.set_runs([SortRun(ALGORITHMS["bubble"], [2, 1])])
    while not player.all_done:
        player.step()
    player.toggle()
    assert player.playing
    assert player.runs[0].stats.steps == 0
    player.pause()

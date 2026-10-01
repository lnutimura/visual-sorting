import random

import pytest

from visual_sorting.algorithms import ALGORITHMS
from visual_sorting.distributions import DISTRIBUTIONS
from visual_sorting.player import SortRun

SIZES = [0, 1, 2, 3, 17, 64, 257]


@pytest.mark.parametrize("size", SIZES)
@pytest.mark.parametrize("distribution", DISTRIBUTIONS)
@pytest.mark.parametrize("key", ALGORITHMS)
def test_sorts(key, distribution, size):
    values = DISTRIBUTIONS[distribution](size, random.Random(size))
    run = SortRun(ALGORITHMS[key], values)
    while not run.done:
        run.advance(10_000)
    assert run.array == sorted(values)


@pytest.mark.parametrize("key", ALGORITHMS)
def test_events_stay_in_bounds(key):
    run = SortRun(ALGORITHMS[key], DISTRIBUTIONS["Random"](50, random.Random(0)))
    while run.advance(1):
        assert all(0 <= i < 50 for i in run.compared + run.written)


def test_worst_case_quicksort_does_not_recurse():
    run = SortRun(ALGORITHMS["quick_left"], list(range(3000)))
    while not run.done:
        run.advance(1_000_000)
    assert run.array == list(range(3000))


@pytest.mark.parametrize("distribution", DISTRIBUTIONS)
def test_distributions_have_requested_size_and_range(distribution):
    values = DISTRIBUTIONS[distribution](100, random.Random(1))
    assert len(values) == 100
    assert all(1 <= v <= 100 for v in values)

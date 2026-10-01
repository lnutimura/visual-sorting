"""Events emitted by sorting algorithms.

Algorithms are generators that read from the array they are given but never
write to it. Instead they yield ``Swap``/``Write`` events, and whoever drives
the generator must apply each one (see ``player.SortRun``) before resuming
it. This keeps the drawn array and the algorithm's view of it identical.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Compare:
    i: int
    j: int


@dataclass(frozen=True, slots=True)
class Swap:
    i: int
    j: int


@dataclass(frozen=True, slots=True)
class Write:
    i: int
    value: int


Event = Compare | Swap | Write
EventStream = Iterator[Event]


def compare_swap(arr: Sequence[int], i: int, j: int) -> EventStream:
    """Compare ``arr[i]`` and ``arr[j]`` and swap them if out of order."""
    yield Compare(i, j)
    if arr[i] > arr[j]:
        yield Swap(i, j)

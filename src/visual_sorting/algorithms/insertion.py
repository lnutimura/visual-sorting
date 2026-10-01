"""Insertion sorts. Elements are moved by swaps so the array stays a valid
permutation at every frame (no duplicated "ghost" values on screen)."""

from __future__ import annotations

from collections.abc import Sequence

from visual_sorting.events import Compare, EventStream, Swap


def gapped_insertion(a: Sequence[int], lo: int, hi: int, gap: int = 1) -> EventStream:
    """Insertion sort over ``a[lo:hi]`` using stride ``gap``."""
    for i in range(lo + gap, hi):
        j = i
        while j - gap >= lo:
            yield Compare(j - gap, j)
            if a[j - gap] <= a[j]:
                break
            yield Swap(j - gap, j)
            j -= gap


def insertion_sort(a: Sequence[int]) -> EventStream:
    yield from gapped_insertion(a, 0, len(a))


def shell_sort(a: Sequence[int]) -> EventStream:
    """Shell sort with gaps 2^k - 1 (Hibbard), as in the 2018 version."""
    gaps = []
    k = 1
    while (1 << k) - 1 < len(a):
        gaps.append((1 << k) - 1)
        k += 1
    for gap in reversed(gaps or [1]):
        yield from gapped_insertion(a, 0, len(a), gap)

"""Sorting networks: a fixed sequence of compare-exchange operations."""

from __future__ import annotations

from collections.abc import Sequence

from visual_sorting.events import Compare, EventStream, Swap


def _compare_exchange(a: Sequence[int], i: int, j: int, ascending: bool) -> EventStream:
    yield Compare(i, j)
    if (a[i] > a[j]) == ascending and a[i] != a[j]:
        yield Swap(i, j)


def _bitonic_merge(a: Sequence[int], lo: int, n: int, ascending: bool) -> EventStream:
    if n < 2:
        return
    m = 1 << ((n - 1).bit_length() - 1)
    for i in range(lo, lo + n - m):
        yield from _compare_exchange(a, i, i + m, ascending)
    yield from _bitonic_merge(a, lo, m, ascending)
    yield from _bitonic_merge(a, lo + m, n - m, ascending)


def _bitonic_sort(a: Sequence[int], lo: int, n: int, ascending: bool) -> EventStream:
    if n < 2:
        return
    m = n // 2
    yield from _bitonic_sort(a, lo, m, not ascending)
    yield from _bitonic_sort(a, lo + m, n - m, ascending)
    yield from _bitonic_merge(a, lo, n, ascending)


def bitonic_sort(a: Sequence[int]) -> EventStream:
    """Bitonic sort generalised to any ``n`` (H. W. Lang's variant)."""
    yield from _bitonic_sort(a, 0, len(a), True)

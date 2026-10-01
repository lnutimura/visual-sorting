"""Partition-based sorts. Recursion is replaced by an explicit stack so a
worst-case (e.g. leftmost pivot on sorted input) cannot hit Python's
recursion limit."""

from __future__ import annotations

import math
from collections.abc import Generator, Sequence

from visual_sorting.algorithms.insertion import gapped_insertion
from visual_sorting.algorithms.selection import heap_sort_range
from visual_sorting.events import Compare, Event, EventStream, Swap, compare_swap


def _partition(a: Sequence[int], left: int, right: int, p: int) -> Generator[Event, None, tuple[int, int]]:
    """Hoare-style partition of ``a[left..right]`` around the value at ``p``.

    Returns ``(d, u)``: ``a[left..u]`` <= pivot <= ``a[d..right]``.
    """
    pivot = a[p]
    d, u = left, right
    while d <= u:
        while True:
            yield Compare(d, p)
            if a[d] >= pivot:
                break
            d += 1
        while True:
            yield Compare(u, p)
            if a[u] <= pivot:
                break
            u -= 1
        if d <= u:
            if d != u:
                yield Swap(d, u)
                if p == d:
                    p = u
                elif p == u:
                    p = d
            d += 1
            u -= 1
    return d, u


def _quick_sort(a: Sequence[int], middle_pivot: bool) -> EventStream:
    stack = [(0, len(a) - 1)] if len(a) > 1 else []
    while stack:
        left, right = stack.pop()
        p = (left + right) // 2 if middle_pivot else left
        d, u = yield from _partition(a, left, right, p)
        if d < right:
            stack.append((d, right))
        if left < u:
            stack.append((left, u))


def quick_sort_leftmost(a: Sequence[int]) -> EventStream:
    yield from _quick_sort(a, middle_pivot=False)


def quick_sort_middle(a: Sequence[int]) -> EventStream:
    yield from _quick_sort(a, middle_pivot=True)


INTRO_SMALL = 16


def intro_sort(a: Sequence[int]) -> EventStream:
    """Median-of-three quicksort that falls back to heap sort when recursion
    gets too deep, and to insertion sort on small ranges."""
    n = len(a)
    if n < 2:
        return
    stack = [(0, n, 2 * int(math.log2(n)))]
    while stack:
        lo, hi, depth = stack.pop()
        if hi - lo <= INTRO_SMALL:
            yield from gapped_insertion(a, lo, hi)
            continue
        if depth == 0:
            yield from heap_sort_range(a, lo, hi)
            continue
        mid = (lo + hi - 1) // 2
        yield from compare_swap(a, lo, mid)
        yield from compare_swap(a, mid, hi - 1)
        yield from compare_swap(a, lo, mid)
        d, u = yield from _partition(a, lo, hi - 1, mid)
        if d < hi - 1:
            stack.append((d, hi, depth - 1))
        if lo < u:
            stack.append((lo, u + 1, depth - 1))

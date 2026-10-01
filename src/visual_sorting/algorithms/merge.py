"""Merge-based sorts. Merging uses auxiliary copies, so the array is updated
with ``Write`` events rather than swaps."""

from __future__ import annotations

from collections.abc import Sequence

from visual_sorting.algorithms.insertion import gapped_insertion
from visual_sorting.events import Compare, EventStream, Swap, Write


def merge(a: Sequence[int], lo: int, mid: int, hi: int) -> EventStream:
    """Merge the sorted runs ``a[lo:mid]`` and ``a[mid:hi]``."""
    left = list(a[lo:mid])
    right = list(a[mid:hi])
    i = j = 0
    k = lo
    while i < len(left) and j < len(right):
        yield Compare(lo + i, mid + j)
        if left[i] <= right[j]:
            yield Write(k, left[i])
            i += 1
        else:
            yield Write(k, right[j])
            j += 1
        k += 1
    for value in left[i:]:
        yield Write(k, value)
        k += 1
    for value in right[j:]:
        yield Write(k, value)
        k += 1


def _merge_sort(a: Sequence[int], lo: int, hi: int) -> EventStream:
    if hi - lo < 2:
        return
    mid = (lo + hi) // 2
    yield from _merge_sort(a, lo, mid)
    yield from _merge_sort(a, mid, hi)
    yield from merge(a, lo, mid, hi)


def merge_sort(a: Sequence[int]) -> EventStream:
    yield from _merge_sort(a, 0, len(a))


def _min_run(n: int) -> int:
    r = 0
    while n >= 64:
        r |= n & 1
        n >>= 1
    return n + r


def tim_sort(a: Sequence[int]) -> EventStream:
    """Simplified Timsort: natural runs (descending ones reversed) extended to
    ``minrun`` with insertion sort, then merged pairwise. No galloping."""
    n = len(a)
    if n < 2:
        return
    min_run = _min_run(n)
    runs = []
    start = 0
    while start < n:
        end = start + 1
        if end < n:
            yield Compare(start, end)
            if a[end] < a[start]:
                while end + 1 < n:
                    yield Compare(end, end + 1)
                    if a[end + 1] >= a[end]:
                        break
                    end += 1
                end += 1
                for i in range((end - start) // 2):
                    yield Swap(start + i, end - 1 - i)
            else:
                while end + 1 < n:
                    yield Compare(end, end + 1)
                    if a[end + 1] < a[end]:
                        break
                    end += 1
                end += 1
        forced_end = min(start + min_run, n)
        if end < forced_end:
            yield from gapped_insertion(a, start, forced_end)
            end = forced_end
        runs.append((start, end))
        start = end

    while len(runs) > 1:
        merged = []
        for k in range(0, len(runs) - 1, 2):
            lo, mid = runs[k]
            _, hi = runs[k + 1]
            yield from merge(a, lo, mid, hi)
            merged.append((lo, hi))
        if len(runs) % 2:
            merged.append(runs[-1])
        runs = merged

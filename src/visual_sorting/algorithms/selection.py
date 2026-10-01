"""Selection sorts: repeatedly pick the extreme element of the unsorted part."""

from __future__ import annotations

from collections.abc import Sequence

from visual_sorting.events import Compare, EventStream, Swap


def selection_sort(a: Sequence[int]) -> EventStream:
    n = len(a)
    for i in range(n - 1):
        smallest = i
        for j in range(i + 1, n):
            yield Compare(j, smallest)
            if a[j] < a[smallest]:
                smallest = j
        if smallest != i:
            yield Swap(i, smallest)


def _sift_down(a: Sequence[int], lo: int, size: int, root: int) -> EventStream:
    """Sift ``root`` down in the max-heap stored in ``a[lo:lo + size]``."""
    while True:
        largest = root
        for child in (2 * root + 1, 2 * root + 2):
            if child < size:
                yield Compare(lo + child, lo + largest)
                if a[lo + child] > a[lo + largest]:
                    largest = child
        if largest == root:
            return
        yield Swap(lo + root, lo + largest)
        root = largest


def heap_sort_range(a: Sequence[int], lo: int, hi: int) -> EventStream:
    size = hi - lo
    for root in range(size // 2 - 1, -1, -1):
        yield from _sift_down(a, lo, size, root)
    for end in range(size - 1, 0, -1):
        yield Swap(lo, lo + end)
        yield from _sift_down(a, lo, end, 0)


def heap_sort(a: Sequence[int]) -> EventStream:
    yield from heap_sort_range(a, 0, len(a))

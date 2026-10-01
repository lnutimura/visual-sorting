"""Non-comparison sorts: values are bucketed by key and written back."""

from __future__ import annotations

from collections.abc import Sequence

from visual_sorting.events import EventStream, Write


def counting_sort(a: Sequence[int]) -> EventStream:
    if not a:
        return
    lo = min(a)
    counts = [0] * (max(a) - lo + 1)
    for value in a:
        counts[value - lo] += 1
    k = 0
    for offset, count in enumerate(counts):
        for _ in range(count):
            yield Write(k, lo + offset)
            k += 1


def radix_sort_lsd(a: Sequence[int], base: int = 10) -> EventStream:
    if not a:
        return
    lo = min(a)
    span = max(a) - lo
    place = 1
    while True:
        buckets: list[list[int]] = [[] for _ in range(base)]
        for value in a:
            buckets[(value - lo) // place % base].append(value)
        k = 0
        for bucket in buckets:
            for value in bucket:
                yield Write(k, value)
                k += 1
        place *= base
        if place > span:
            return

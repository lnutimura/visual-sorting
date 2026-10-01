"""Exchange sorts: neighbours (or gapped pairs) are compared and swapped."""

from __future__ import annotations

from collections.abc import Sequence

from visual_sorting.events import Compare, EventStream, Swap


def unflagged_bubble_sort(a: Sequence[int]) -> EventStream:
    n = len(a)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            yield Compare(j, j + 1)
            if a[j] > a[j + 1]:
                yield Swap(j, j + 1)


def flagged_bubble_sort(a: Sequence[int]) -> EventStream:
    n = len(a)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            yield Compare(j, j + 1)
            if a[j] > a[j + 1]:
                yield Swap(j, j + 1)
                swapped = True
        if not swapped:
            return


def cocktail_shaker_sort(a: Sequence[int]) -> EventStream:
    lo, hi = 0, len(a) - 1
    while lo < hi:
        last = lo
        for j in range(lo, hi):
            yield Compare(j, j + 1)
            if a[j] > a[j + 1]:
                yield Swap(j, j + 1)
                last = j
        hi = last
        last = hi
        for j in range(hi, lo, -1):
            yield Compare(j - 1, j)
            if a[j - 1] > a[j]:
                yield Swap(j - 1, j)
                last = j
        lo = last


def comb_sort(a: Sequence[int]) -> EventStream:
    n = len(a)
    gap = n
    done = False
    while not done:
        gap = max(1, int(gap / 1.3))
        done = gap == 1
        for i in range(n - gap):
            yield Compare(i, i + gap)
            if a[i] > a[i + gap]:
                yield Swap(i, i + gap)
                done = False


def gnome_sort(a: Sequence[int]) -> EventStream:
    pos = 0
    while pos < len(a):
        if pos == 0:
            pos += 1
            continue
        yield Compare(pos - 1, pos)
        if a[pos - 1] <= a[pos]:
            pos += 1
        else:
            yield Swap(pos - 1, pos)
            pos -= 1


def odd_even_sort(a: Sequence[int]) -> EventStream:
    n = len(a)
    done = False
    while not done:
        done = True
        for start in (1, 0):
            for i in range(start, n - 1, 2):
                yield Compare(i, i + 1)
                if a[i] > a[i + 1]:
                    yield Swap(i, i + 1)
                    done = False

"""Registry of every algorithm the app can visualise."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from visual_sorting.algorithms import distribution, exchange, insertion, merge, network, quick, selection
from visual_sorting.events import EventStream


@dataclass(frozen=True)
class Algorithm:
    key: str
    name: str
    family: str
    run: Callable[[Sequence[int]], EventStream]
    complexity: str
    description: str


_ALL = [
    Algorithm("bubble", "Bubble Sort (unflagged)", "Exchange", exchange.unflagged_bubble_sort, "O(n²)",
              "Sweeps the array swapping neighbours that are out of order, always doing every pass."),
    Algorithm("bubble_flagged", "Bubble Sort (flagged)", "Exchange", exchange.flagged_bubble_sort, "O(n²)",
              "Bubble sort that stops as soon as a full pass makes no swaps."),
    Algorithm("cocktail", "Cocktail Shaker Sort", "Exchange", exchange.cocktail_shaker_sort, "O(n²)",
              "Bubble sort that alternates direction, moving small values left as fast as large ones right."),
    Algorithm("comb", "Comb Sort", "Exchange", exchange.comb_sort, "O(n² / 2^p)",
              "Bubble sort over a gap that shrinks by 1.3 each pass, killing 'turtles' early."),
    Algorithm("gnome", "Gnome Sort", "Exchange", exchange.gnome_sort, "O(n²)",
              "Walks forward while in order, and steps back swapping when it finds an inversion."),
    Algorithm("odd_even", "Odd-Even Sort", "Exchange", exchange.odd_even_sort, "O(n²)",
              "Alternates compare-swaps on odd and even neighbour pairs; a parallel-friendly bubble sort."),
    Algorithm("insertion", "Insertion Sort", "Insertion", insertion.insertion_sort, "O(n²)",
              "Grows a sorted prefix by sinking each new element back into place."),
    Algorithm("shell", "Shell Sort", "Insertion", insertion.shell_sort, "O(n^1.5)",
              "Insertion sort over shrinking gaps 2^k - 1, so elements travel far in few moves."),
    Algorithm("selection", "Selection Sort", "Selection", selection.selection_sort, "O(n²)",
              "Finds the minimum of the unsorted part and swaps it to the front."),
    Algorithm("heap", "Heap Sort", "Selection", selection.heap_sort, "O(n log n)",
              "Builds a max-heap, then repeatedly moves the root to the end and repairs the heap."),
    Algorithm("quick_left", "Quick Sort (leftmost pivot)", "Partition", quick.quick_sort_leftmost, "O(n log n)",
              "Hoare partition around the first element. Degrades to O(n²) on sorted input."),
    Algorithm("quick_middle", "Quick Sort (middle pivot)", "Partition", quick.quick_sort_middle, "O(n log n)",
              "Hoare partition around the middle element, robust on already-sorted input."),
    Algorithm("intro", "Introsort", "Partition", quick.intro_sort, "O(n log n)",
              "Median-of-three quicksort with a heap sort fallback and insertion sort for small ranges."),
    Algorithm("merge", "Merge Sort", "Merge", merge.merge_sort, "O(n log n)",
              "Recursively sorts both halves, then merges them through an auxiliary buffer."),
    Algorithm("tim", "Timsort (simplified)", "Merge", merge.tim_sort, "O(n log n)",
              "Detects natural runs, extends short ones with insertion sort, then merges runs pairwise."),
    Algorithm("counting", "Counting Sort", "Distribution", distribution.counting_sort, "O(n + k)",
              "Counts occurrences of each value and writes them back in order. No comparisons."),
    Algorithm("radix", "Radix Sort (LSD, base 10)", "Distribution", distribution.radix_sort_lsd, "O(d·n)",
              "Stable bucket passes on each decimal digit, least significant first. No comparisons."),
    Algorithm("bitonic", "Bitonic Sort", "Network", network.bitonic_sort, "O(n log² n)",
              "A fixed sorting network of compare-exchanges, generalised to any array size."),
]

ALGORITHMS: dict[str, Algorithm] = {algo.key: algo for algo in _ALL}

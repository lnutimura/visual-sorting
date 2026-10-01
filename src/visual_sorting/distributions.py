"""Input generators. Each returns ``n`` integers in ``1..n``."""

from __future__ import annotations

import random
from collections.abc import Callable


def shuffled(n: int, rng: random.Random) -> list[int]:
    values = list(range(1, n + 1))
    rng.shuffle(values)
    return values


def sorted_values(n: int, rng: random.Random) -> list[int]:
    return list(range(1, n + 1))


def reversed_values(n: int, rng: random.Random) -> list[int]:
    return list(range(n, 0, -1))


def nearly_sorted(n: int, rng: random.Random) -> list[int]:
    values = list(range(1, n + 1))
    window = max(2, n // 20)
    for _ in range(max(1, n // 10)):
        if n < 2:
            break
        i = rng.randrange(n)
        j = min(n - 1, max(0, i + rng.randint(-window, window)))
        values[i], values[j] = values[j], values[i]
    return values


def few_unique(n: int, rng: random.Random, levels: int = 6) -> list[int]:
    levels = max(1, min(levels, n))
    values = [1 + (i * levels // max(n, 1)) * n // levels for i in range(n)]
    rng.shuffle(values)
    return values


def sawtooth(n: int, rng: random.Random, teeth: int = 4) -> list[int]:
    tooth = max(1, -(-n // teeth))
    return [1 + (i % tooth) * n // tooth for i in range(n)]


DISTRIBUTIONS: dict[str, Callable[[int, random.Random], list[int]]] = {
    "Random": shuffled,
    "Reversed": reversed_values,
    "Nearly sorted": nearly_sorted,
    "Few unique": few_unique,
    "Sorted": sorted_values,
    "Sawtooth": sawtooth,
}

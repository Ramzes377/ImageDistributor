from dataclasses import dataclass, fields
from typing import Callable

import numba


@numba.njit(fastmath=True)
def euclidian(x, y, r) -> float:
    return ((r - x) ** 2 + (r - y) ** 2) ** 0.5


@numba.njit(fastmath=True)
def chebyshev(x, y, r) -> float:
    return max(abs(r - x), abs(r - y))


@numba.njit(fastmath=True)
def combine(x, y, r) -> float:
    return 0.5 * (euclidian(x, y, r) + chebyshev(x, y, r))


@numba.njit(fastmath=True)
def canverra(x, y, r) -> float:
    return r * (abs(r - x) / (abs(x) + r) + abs(r - y) / (abs(y) + r))


@numba.njit(fastmath=True)
def taxicab(x, y, r) -> float:
    return abs(r - x) + abs(r - y)


@numba.njit(fastmath=True)
def cosine(x: int, y: int, r: int, k: int = 1220) -> float:
    return k * (1 - (r * x + r * y) / (r * 2 ** 0.5 * (x * x + y * y) ** 0.5))


@dataclass(frozen=True, slots=True)
class Metric:
    metric_func: Callable
    name: str


metric_mapping = {
    '': 'euclidian',
    'Круглый': 'euclidian',
    'Квадратный': 'chebyshev',
    'Смешанный': 'combine',
    'ПсевдоКруглый': 'canverra',
    'Ромбовидный': 'taxicab',
    'Звезда': 'cosine',
    # 'euclidian': 'euclidian',
    # 'chebyshev': 'chebyshev',
    # 'combine': 'combine',
    # 'canverra': 'canverra',
    # 'taxicab': 'taxicab',
    # 'cosine': 'cosine',
}


@dataclass(frozen=True, slots=True)
class MetricFunctions:
    euclidian: Metric = Metric(euclidian, name='Круглый')
    chebyshev: Metric = Metric(chebyshev, name='Квадратный')
    combine: Metric = Metric(combine, name='Смешанный')
    canverra: Metric = Metric(canverra, name='ПсевдоКруглый')
    taxicab: Metric = Metric(taxicab, name='Ромбовидный')
    cosine: Metric = Metric(cosine, name='Звезда')

    def __iter__(self):
        for field in fields(self):
            yield getattr(self, field.name).name


metrics = MetricFunctions()

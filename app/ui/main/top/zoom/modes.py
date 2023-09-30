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
def cosine(x, y, r) -> float:
    a = (r, r)
    b = (x, y)
    a_l = 2 ** 0.5 * r
    b_l = (b[0] * b[0] + b[1] * b[1]) ** 0.5
    brightness = 1220 * (1 - (a[0] * b[0] + a[1] * b[1]) / (a_l * b_l))
    return brightness


class GetItemMeta(type):
    _modes: dict[int: str] = None
    _map: tuple[str] = (
        'Круглый',
        'Квадратный',
        'Смешанный',
        'ПсевдоКруглый',
        'Ромбовидный',
        'Звезда'
    )

    def __getitem__(mcs, item):
        return getattr(mcs, mcs._modes[item])

    def __iter__(self):
        yield from self._map


class SlottedModes(metaclass=GetItemMeta):
    __slots__ = (
        'euclidian',
        'chebyshev',
        'combine',
        'canverra',
        'taxicab',
        'cosine'
    )

    _modes = dict(zip(range(6), __slots__))


class DistanceMode(SlottedModes):
    euclidian = euclidian
    chebyshev = chebyshev
    combine = combine
    canverra = canverra
    taxicab = taxicab
    cosine = cosine

import numba


@numba.njit(fastmath=True)
def euclidian(x, y, r):
    return ((r - x) ** 2 + (r - y) ** 2) ** 0.5


@numba.njit(fastmath=True)
def chebyshev(x, y, r):
    return max(abs(r - x), abs(r - y))


@numba.njit(fastmath=True)
def combine(x, y, r):
    return 0.5 * (euclidian(x, y, r) + chebyshev(x, y, r))


@numba.njit(fastmath=True)
def canverra(x, y, r):
    return r * (abs(r - x) / (abs(x) + r) + abs(r - y) / (abs(y) + r))


@numba.njit(fastmath=True)
def taxicab(x, y, r):
    return abs(r - x) + abs(r - y)


@numba.njit(fastmath=True)
def cosine(x, y, r):
    a = (r, r)
    b = (x, y)
    a_l = 2 ** 0.5 * r
    b_l = (b[0] * b[0] + b[1] * b[1]) ** 0.5
    brightness = 1220 * (1 - (a[0] * b[0] + a[1] * b[1]) / (a_l * b_l))
    return brightness


calculation_methods = {
    0: euclidian,
    1: chebyshev,
    2: combine,
    3: canverra,
    4: taxicab,
    5: cosine
}

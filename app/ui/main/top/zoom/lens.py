from typing import Iterable, Callable

import numba
import numpy as np
from PIL import Image

from .modes import DistanceMode


@numba.njit(fastmath=True)
def lerp(s, e, a):
    return (1 - a) * s + e * a


@numba.njit(fastmath=True)
def get_mask_array(
        calc: Callable,
        diameter: int,
        ratio: float,
        start_value: int,
        end_value: int,
):
    radius = int(diameter // 2)
    start_point = radius * ratio + 1
    end_point = radius

    start_value = int(start_value * 2.55)
    end_value = int(end_value * 2.55)

    length = end_point - start_point

    out = np.zeros((diameter, diameter), dtype=np.uint8)

    for x in range(1, radius + 1):
        for y in range(x, radius + 1):

            distance = calc(x, y, radius)
            val = 0

            if distance <= end_point:
                if distance <= start_point:
                    val = start_value
                else:
                    amount = (distance - start_point) / length
                    val = lerp(start_value, end_value, amount)

            out[x][y] = out[-x - 1][y] = out[-x - 1][-y - 1] = \
                out[x][-y - 1] = out[y][x] = out[-y - 1][x] = \
                out[-y - 1][-x - 1] = out[y][-x - 1] = val
    return out


class Lens:
    default = (0, 300, 2 / 3, 88, 1)
    mask: Image = None
    diameter: float = 0

    def __init__(self):
        self.__call__(Lens.default)

    def __call__(self, gen: Iterable):
        # using call method to generate new lens mask
        self.mask, self.diameter = Lens.get_mask(gen)

    @staticmethod
    def get_mask(gen: Iterable) -> (Image, float):
        mode, diameter, *params = tuple(gen)
        mode = DistanceMode[mode]
        return (
            Image.fromarray(get_mask_array(mode, diameter, *params), 'L'),
            diameter
        )

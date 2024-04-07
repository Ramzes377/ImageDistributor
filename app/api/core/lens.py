from typing import Callable, Literal, Any

import numba
import numpy as np
from PIL import Image
from pydantic import BaseModel, model_validator, Field

from app.api.core.lens_modes import metrics


@numba.njit(fastmath=True)
def lerp(s, e, a):
    return (1 - a) * s + e * a


@numba.njit(fastmath=True)
def get_mask_array(
        mode: Callable,
        diameter: int,
        ratio: float,
        inner_brightness: int,
        outer_brightness: int,
):
    radius = int(diameter // 2)
    start_point = radius * ratio + 1
    end_point = radius

    length = end_point - start_point

    out = np.zeros((diameter, diameter), dtype=np.uint8)

    for x in range(1, radius + 1):
        for y in range(x, radius + 1):

            distance = mode(x, y, radius)
            val = 0

            if distance <= end_point:
                if distance <= start_point:
                    val = inner_brightness
                else:
                    amount = (distance - start_point) / length
                    val = lerp(inner_brightness, outer_brightness, amount)

            out[x][y] = out[-x - 1][y] = out[-x - 1][-y - 1] = \
                out[x][-y - 1] = out[y][x] = out[-y - 1][x] = \
                out[-y - 1][-x - 1] = out[y][-x - 1] = val
    return out


class Lens(BaseModel):
    mode: Literal[
        'euclidian',
        'chebyshev',
        'combine',
        'canverra',
        'taxicab',
        'cosine',
    ] = 'euclidian'
    diameter: int = 300
    ratio: float = 0.66
    inner_brightness: int = 220
    outer_brightness: int = 255

    mask: Any = Field(default=None, exclude=True)

    @model_validator(mode='after')
    def validate(cls, self):
        data = self.model_dump()
        data['mode'] = getattr(metrics, self.mode).metric_func
        self.mask = Image.fromarray(get_mask_array(**data), 'L')
        return self

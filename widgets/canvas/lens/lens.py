import numba
from PIL import Image
import numpy as np
from .distancemodes import calculation_methods

@numba.njit(fastmath=True)
def get_mask_array(d, ratio, start_value, end_value, point_brightness):
    r = int(d//2)
    start_point = r * ratio + 1
    end_point = r
    lenght = end_point - start_point
    start_value = int(start_value * 2.55)
    end_value = int(end_value * 2.55)
    r = int(d//2)
    out = np.zeros((d, d), dtype=np.uint8)
    for x in range(1, r + 1):
        for y in range(x, r + 1):
            distance = point_brightness(x, y, r)
            val = 0
            if distance <= end_point:
                val = start_value if distance <= start_point else lerp(start_value, end_value, (distance - start_point) / lenght )
            out[x][y] = out[-x - 1][y] = out[-x - 1][-y - 1] = out[x][-y - 1] = out[y][x] = out[-y - 1][x] = \
                out[-y - 1][-x - 1] = out[y][-x - 1] = val
    return out

@numba.njit(fastmath=True)
def lerp(s, e, a):
    return (1 - a)*s + e*a

class Lens:
    def __init__(self):
        self((0, 300, 2/3, 88, 1)) #initiate standart lens

    def __call__(self, gen):
        self._mask, self._diameter = self.get_mask(gen)

    mask = property(lambda self: self._mask, __call__)

    def get_mask(self, gen):
        mode, d, ratio, start_value, end_value = tuple(gen)
        diameter = int(d)
        mode = calculation_methods[mode]
        return Image.fromarray(get_mask_array(diameter, ratio, start_value, end_value, mode), 'L'), diameter


lens = Lens()



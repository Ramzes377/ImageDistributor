from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from app.ui.main.top.display import ImageFrame


@dataclass
class ZoomData:
    parent: 'ImageFrame'

    scale: float = 0.0
    min_scale: float = 0.0
    _scale_multiplier: float = 1 / 1200

    max_ratio: float = 1.0

    lens: Any = None

    def __post_init__(self):
        from app.api.container import container

        self.lens = container.lens_settings

    @property
    def corrected_diameter(self) -> int:
        return int(min(self.lens.diameter // self.max_ratio, self.lens.diameter))

    def __call__(self):
        W, H = self.original.size
        self.max_ratio = W / self.w if W > H else H / self.h

        mask, d = self.lens.mask, self.lens.diameter
        self.min_scale = max(d / max(self.original.size), 2 ** .5) - 0.01

        self.scale = self.min_scale

        self.top_left_corner = 0.5 * (self.resolution - self.parent.size)
        self.bot_right_corner = 0.5 * (self.resolution + self.parent.size)

    def get_crop_boundary(self, center: np.array) -> np.array:
        k = 0.5 * self.max_ratio

        projection = k * (2 * center - self.resolution + self.parent.size)
        view_delta = int(self.lens.diameter / (self.scale ** 2))
        area = np.hstack((projection - view_delta, projection + view_delta))

        border = np.array(self.original.size)

        r = self.corrected_diameter / 2

        left_top_group = self.top_left_corner - center
        right_bottom_group = self.bot_right_corner - center

        lt_cond = left_top_group > -r
        rb_cond = right_bottom_group < r

        if lt_cond[0]:
            if area[0] < 0:
                area[0] = 0
                area[2] = 2 * view_delta
            center[0] = self.top_left_corner[0] + r
        if lt_cond[1]:
            if area[1] < 0:
                area[1] = 0
                area[3] = 2 * view_delta
            center[1] = self.top_left_corner[1] + r + 1
        if rb_cond[0]:
            if border[0] < area[2]:
                area[0] = border[0] - 2 * view_delta
                area[2] = border[0]
            center[0] = self.bot_right_corner[0] - r - 1
        if rb_cond[1]:
            if border[1] < area[3]:
                area[1] = border[1] - 2 * view_delta
                area[3] = border[1]
            center[1] = self.bot_right_corner[1] - r

        return area

    @property
    def scale_radius(self) -> float:
        return 0.5 * (self.scale - self.min_scale + 0.2) ** 2

    def update_scale(self, value: float) -> None:
        value *= self._scale_multiplier
        self.scale = max(self.min_scale, self.scale + value)

    @property
    def original(self):
        return self.parent.original

    @property
    def w(self):
        return self.parent.w

    @property
    def h(self):
        return self.parent.h

    @property
    def resolution(self) -> np.array:
        return np.array([self.w, self.h])

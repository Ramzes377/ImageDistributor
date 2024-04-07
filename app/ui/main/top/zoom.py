from contextlib import suppress
from dataclasses import dataclass, field
from typing import Callable, Any, TYPE_CHECKING

import numpy as np
from PIL import ImageTk, ImageFilter

from app.api.core.zoom import ZoomData

if TYPE_CHECKING:
    from app.ui.main.top.display import ImageFrame


@dataclass
class Zoom:
    parent: 'ImageFrame'
    redraw: Callable

    zoom_img_id: int = None
    zoom_img: ImageTk = None

    side_img: ImageTk = None
    side_crop: ImageTk = None

    zoom_data: ZoomData = field(init=False)

    lens: Any = None

    def __post_init__(self):
        from app.api.container import container

        self.zoom_data = ZoomData(parent=self.parent)
        self.lens = container.lens_settings

    @property
    def original(self):
        return self.parent.original

    def __call__(self):
        if self.original is None:
            return

        self.zoom_data.__call__()
        self.redraw()

    def zoomer(self, event) -> None:
        if self.original is None:
            return

        self.zoom_data.update_scale(event.delta)
        self.crop(event)

    def crop(self, event):

        if self.original is None:
            return

        if self.zoom_data.scale <= self.zoom_data.min_scale:
            self.parent.configure(cursor='arrow')
            self.clear()
            return

        self.parent.configure(cursor='none')
        center = np.array([event.x, event.y])

        crop_area = self.zoom_data.get_crop_boundary(center)

        mask, d = self.lens.mask, self.lens.diameter
        lens_img = self.original.crop(crop_area).resize((d, d))

        blured_lens = lens_img.filter(
            ImageFilter.BoxBlur(
                radius=self.zoom_data.scale_radius
            )
        )
        blured_lens.putalpha(mask)

        diam = self.zoom_data.corrected_diameter
        self.zoom_img = ImageTk.PhotoImage(blured_lens.resize((diam, diam)))
        self.zoom_img_id = self.parent.display.create_image(
            *center,
            image=self.zoom_img
        )

        r = int(min(self.w, self.h) / 3)
        self.side_img = ImageTk.PhotoImage(lens_img.resize((r, r)))
        self.side_crop = self.parent.display.create_image(
            self.w - r / 2,
            self.h - r / 2,
            image=self.side_img
        )

    def clear(self):
        with suppress(AttributeError):
            self.parent.display.delete(self.zoom_img_id)

        with suppress(AttributeError):
            self.parent.display.delete(self.side_crop)

    @property
    def w(self):
        return self.parent.w

    @property
    def h(self):
        return self.parent.h

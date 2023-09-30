import tkinter
from contextlib import suppress
from typing import Callable

from PIL import ImageTk, ImageFilter
from customtkinter import CTkFrame

from .lens import Lens


class Zoom:

    def __init__(self, parent: CTkFrame, redraw: Callable):
        self._zimg_id = None
        self._zimg = None
        self.im = None
        self.side_crop = None
        self.parent = parent
        self._zoomcycle = -1
        self._min_zoom = -2
        self._redraw = redraw
        self._dt = 1

        self.lens = Lens()

    @property
    def original(self):
        return self.parent.original

    def __call__(self):

        W, H = self.original.size
        self._dt = W / self.parent.w if W > H else H / self.parent.h

        mask, d = self.lens.mask, self.lens.diameter
        self._min_zoom = max(d / max(self.original.size), 2 ** .5) - 0.01

        self._zoomcycle = self._min_zoom

        size = self.parent.size

        self.top_left_corner = .5 * (self.w - size[0]), .5 * (self.h - size[1])
        self.bot_right_corner = .5 * (self.w + size[0]), .5 * (self.h + size[1])

    def zoomer(self, event):
        if not self.original:
            return

        self._zoomcycle += event.delta / 1200
        if self.original:
            if self._zoomcycle < self._min_zoom:
                self._zoomcycle = self._min_zoom

    @staticmethod
    def is_cursor_in_pic(crop_area, border, dt) -> bool:
        return (
                crop_area[0] > -dt and
                crop_area[1] > -dt and
                crop_area[2] < border[0] + dt and
                crop_area[3] < border[1] + dt
        )

    def get_crop_boundary(self, center, d, area, border, dt):
        x, y = center
        nd = min(int(d / self._dt), d)
        r = nd / 2
        if self.top_left_corner[0] > x - r:
            if area[0] < 0:
                area[0] = 0
                area[2] = 2 * dt
            center[0] = self.top_left_corner[0] + r
        elif self.bot_right_corner[0] < x + r:
            if border[0] < area[2]:
                area[0] = border[0] - 2 * dt
                area[2] = border[0]
            center[0] = self.bot_right_corner[0] - r - 1
        if self.top_left_corner[1] > y - r:
            if area[1] < 0:
                area[1] = 0
                area[3] = 2 * dt
            center[1] = self.top_left_corner[1] + r + 1
        elif self.bot_right_corner[1] < y + r:
            if border[1] < area[3]:
                area[1] = border[1] - 2 * dt
                area[3] = border[1]
            center[1] = self.bot_right_corner[1] - r
        return area, nd

    def crop(self, event):

        if not self.original:
            return

        if self._zoomcycle > self._min_zoom:

            self.parent.configure(cursor='none')
            x, y = event.x, event.y

            k = 0.5 * self._dt
            proj = [
                k * (2 * x - self.w + self.parent.size[0]),
                k * (2 * y - self.h + self.parent.size[1])
            ]
            mask, d = self.lens.mask, self.lens.diameter
            dt = int(d / (self._zoomcycle ** 2))

            area = [
                proj[0] - dt,
                proj[1] - dt,
                proj[0] + dt,
                proj[1] + dt
            ]
            border = self.original.size

            if self.is_cursor_in_pic(area, border, dt):
                pos = [x, y]

                area, nd = self.get_crop_boundary(pos, d, area, border, dt)

                lens_img = self.original.crop(area).resize((d, d))

                blured_lens = lens_img.filter(
                    ImageFilter.BoxBlur(
                        radius=
                        0.5 * (self._zoomcycle - self._min_zoom + 0.2) ** 2
                    ))
                blured_lens.putalpha(mask)

                self._zimg = ImageTk.PhotoImage(blured_lens.resize((nd, nd)))
                self._zimg_id = self.parent.display.create_image(
                    x, y,
                    image=self._zimg
                )

                r = int(min(self.w, self.h) / 3)
                self.im = ImageTk.PhotoImage(lens_img.resize((r, r)))
                self.side_crop = self.parent.display.create_image(
                    self.w - r / 2,
                    self.h - r / 2,
                    image=self.im
                )
        else:
            self.parent.configure(cursor='arrow')
            self.clear()

    def clear(self):
        with suppress(AttributeError):
            self.parent.display.delete(self._zimg_id)

        with suppress(AttributeError):
            self.parent.display.delete(self.side_crop)

    @property
    def w(self):
        return self.parent.w

    @property
    def h(self):
        return self.parent.h

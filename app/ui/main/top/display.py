from contextlib import suppress
from tkinter import TclError

import numpy as np
from customtkinter import CTkFrame, CTkCanvas
from PIL import Image, ImageTk, ImageOps

from app.ui.main.top.zoom import Zoom
from app.ui.mixins import _WidgetSizeMixin


class ImageFrame(CTkFrame, _WidgetSizeMixin):
    original: Image = None
    image: ImageTk.PhotoImage = None
    size: np.array = None

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.display = CTkCanvas(self, bg='#2d2d30')
        self.display.grid(sticky='wens')

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.zoom = Zoom(self, self.redraw)
        self.zoom()

        self.display.bind("<Configure>", self.resize)
        self.display.bind("<MouseWheel>", self.zoom.zoomer)
        self.display.bind("<Motion>", self.zoom.crop)

        self.prev_offset = (0, 0)

    def clear(self):
        self.original = None
        self.display.delete("IMG")

    def change_image(self, path: str = None):
        if path is None:
            return self.clear()

        try:
            self.original = Image.open(path)
            self.resize()
        except FileNotFoundError:
            return self.clear()

    @property
    def _image_offset(self) -> (float, float):
        return (
            0.5 * (self.w - self.image.width()),
            0.5 * (self.h - self.image.height())
        )

    def resize(self, event=None):

        if self.original is None:
            return

        size = self.w, self.h

        resized = ImageOps.contain(self.original, size)
        self.image = ImageTk.PhotoImage(resized)
        self.size = np.array(resized.size)
        self.display.delete("IMG")

        self.zoom()
        self.redraw(force=True)

    def redraw(self, force: bool = False):
        with suppress(TclError, AttributeError):
            offset = self._image_offset
            if self.prev_offset != offset or force:
                self.prev_offset = offset
                self.display.create_image(
                    *offset,
                    image=self.image,
                    anchor='nw',
                    tags="IMG"
                )

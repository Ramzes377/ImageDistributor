from contextlib import suppress
from tkinter import TclError

from customtkinter import CTkFrame, CTkCanvas
from PIL import Image, ImageTk, ImageOps

from .zoom import Zoom


class ImageFrame(CTkFrame):
    original: Image = None
    image: ImageTk.PhotoImage = None
    size: tuple[int, int] = None

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.zoom = Zoom(self, self.redraw)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.display = CTkCanvas(self, bg='#2d2d30')
        self.display.grid(sticky='wens')

        self.display.bind("<Configure>", self.resize)
        self.display.bind("<MouseWheel>", self.zoom.zoomer)
        self.display.bind("<Motion>", self.zoom.crop)

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
        self.size = resized.size
        self.display.delete("IMG")
        self.redraw()

    def redraw(self):
        with suppress(TclError):
            self.display.create_image(
                *self._image_offset,
                image=self.image,
                anchor='nw',
                tags="IMG"
            )
            self.zoom()

    @property
    def w(self):
        return self.winfo_width()

    @property
    def h(self):
        return self.winfo_height()

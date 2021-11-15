from PIL import Image, ImageTk

from .zoomer import Zoom
from .basecanvas import BaseCanvas




default = {'bg': '#2d2d30', 'bd': 0, 'highlightthickness': 0, 'relief': 'ridge', 'insertwidth': 10}
class ImageCanvas(BaseCanvas):
    def __init__(self, parent):
        super(ImageCanvas, self).__init__(parent, **default)
        self.zoom = Zoom(self) #create Zoom instance
        self._create_binds_and_packs()

    def change_image(self, filename):
        self._cur_filepath = filename
        try:
            self._original_image = Image.open(self._cur_filepath).convert("RGB")
        except (FileNotFoundError, OSError):
            self._original_image = None
            self.delete(self._prev_img)
            return

        self.update_image()

    def update_image(self):
        self._resized_im = self._original_image.copy()
        self._resized_im.thumbnail((self.w, self.h))
        self._main_tk_img = ImageTk.PhotoImage(self._resized_im)
        self._prev_img = self.create_image(self.w/2 - 1, self.h/2 + 1, image=self._main_tk_img)
        self.zoom() #recalculate zoom main settings

    def _create_binds_and_packs(self, **kw):
        self.bind("<MouseWheel>", self.zoom.zoomer)
        self.bind("<Motion>", self.zoom.crop)
        self.bind("<Configure>", self.resize)
        self.pack(side = 'left', fill="both", expand=True)
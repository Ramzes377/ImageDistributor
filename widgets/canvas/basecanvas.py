from tkinter import Canvas
import numpy as np
from abc import ABC, abstractmethod


class MetaCanvas(ABC):
    @abstractmethod
    def update_image(cls) -> None:
        pass

    @abstractmethod
    def resize(cls, e) -> None:
        #save new size of image that can fit into current window size and update image size
        pass

    @property
    @abstractmethod
    def w(self) -> int:
        #return Width of window
        pass

    @property
    @abstractmethod
    def h(self) -> int:
        #return Height of window
        pass


class BaseCanvas(MetaCanvas, Canvas):
    def __init__(self, *args, **kwargs):
        super(BaseCanvas, self).__init__(*args, **kwargs)
        self._cur_filepath = None
        self._original_image = None
        self._resolution = np.array((200, 150))

    def resize(self, event):
        #Method rewrite current resolution of window and update current image to correspond current size
        self._resolution = np.array((event.__dict__['width'], event.__dict__['height']))
        if self._cur_filepath is not None:
            self.update_image()

    @property
    def w(self):
        return self._resolution[0]

    @property
    def h(self):
        return self._resolution[1]
from tkinter import Widget
from workstuff.globals import *
from abc import ABC, abstractmethod

class mset(set):
    def add(self, a): super(mset, self).add(tuple(sorted(a)))


class MetaWindow(ABC):

    def iconbitmap(self, iconpath):
        pass

    def geometry(self, _geometry: str) -> str:
        pass

    def state(self, _state: str = None) -> str:
        pass

    @abstractmethod
    def switch_state(self):
        pass


class BaseWindow(MetaWindow, Widget):
    def __init__(self, *args, **kwargs):
        super(BaseWindow, self).__init__(*args, **kwargs)
        self._is_hidden = True
        self.deiconify()
        self.withdraw()
        try:
            self.iconbitmap(main_icon)
        except:
            pass
        self.protocol('WM_DELETE_WINDOW', self.switch_state)

    def unhide(self):
        self.config[type(self.master).__name__] = (self.master.winfo_geometry(), self.master.state())

        self._is_hidden = False
        self.master.withdraw()
        self.deiconify()

        try:
            geom, state = self.config[type(self).__name__]
            if state == 'zoomed':
                self.state('zoomed')
            else:
                self.geometry(geom)
        except KeyError:
            pass

    def hide(self):
        self.config[type(self).__name__] = (self.winfo_geometry(), self.state())

        self._is_hidden = True
        self.master.deiconify()
        self.withdraw()

        geom, state = self.config[type(self.master).__name__]
        if state == 'zoomed':
            self.master.state('zoomed')

    def switch_state(self):
        if self._is_hidden:
            self.unhide()
        else:
            self.hide()
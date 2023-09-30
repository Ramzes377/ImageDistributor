from tkinter import Toplevel


class Window(Toplevel):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self._is_hidden = True
        self.deiconify()
        self.withdraw()
        self.protocol('WM_DELETE_WINDOW', self.switch_state)

    def change_directory(self, path: str):
        pass

    def unhide(self):
        self._is_hidden = False
        self.deiconify()

        # try:
        #     geom, state = self.config[type(self).__name__]
        #     if state == 'zoomed':
        #         self.state('zoomed')
        #     else:
        #         self.geometry(geom)
        # except KeyError:
        #     pass

    def hide(self):
        #self.config[type(self).__name__] = (self.winfo_geometry(),
        # self.state())

        self._is_hidden = True
        self.withdraw()

        # geom, state = self.config[type(self.master).__name__]
        # if state == 'zoomed':
        #     self.master.state('zoomed')

    def switch_state(self):
        if self._is_hidden:
            self.unhide()
        else:
            self.hide()
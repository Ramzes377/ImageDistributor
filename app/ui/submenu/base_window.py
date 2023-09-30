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

    def hide(self):
        self._is_hidden = True
        self.withdraw()

    def switch_state(self):
        if self._is_hidden:
            self.unhide()
        else:
            self.hide()

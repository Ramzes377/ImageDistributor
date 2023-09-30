import os
import shutil
from contextlib import suppress

from tkinter import Menu
from customtkinter import CTkButton, CTkFrame

from app.api import container


class MoveButton(CTkButton):

    def __init__(self, master: CTkFrame, path: str, **kwargs):
        super(MoveButton, self).__init__(master, **kwargs)

        self.current_path = path
        self.path = os.path.join(path, self._text)

        menu = Menu(self, tearoff=0)
        menu.add_command(label=f'Убрать кнопку', command=self.pack_forget)
        self.bind("<Button-3>",
                  lambda event: menu.post(event.x_root, event.y_root))

        self.pack(fill='x', expand=0, pady=2)
        self.configure(command=self.move)

    def move(self):
        try:
            file_path = os.path.join(self.current_path, container.current_image)
            dest_path = os.path.join(self.path, container.current_image)
        except TypeError:
            return

        with suppress(FileNotFoundError):
            shutil.move(file_path, dest_path)
        self.master.select_next()  # noqa

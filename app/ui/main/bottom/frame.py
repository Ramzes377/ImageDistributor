import os
from contextlib import suppress
from typing import Iterable, Callable

import customtkinter

from app.ui.main.bottom.button import MoveButton


class DistributeButtonsFrame(customtkinter.CTkFrame):
    select_next: Callable = None
    _buttons = []

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(side='bottom', fill='x', padx=10, pady=10)
        self.render_buttons(os.path.abspath('./'))

    def render_buttons(self, path: str) -> None:
        buttons = (w for name, w in self.children.items() if '!movebutton' in name)
        [b.pack_forget() for b in buttons]

        with suppress(StopIteration):
            folders = next(os.walk(path))[1]
            [
                MoveButton(text=name, master=self, path=path)
                for name in folders if not name.startswith('.')
            ]

    def change_directory(self, path: str):
        self.render_buttons(path)

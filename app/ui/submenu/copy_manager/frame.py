import os
from contextlib import suppress
from pathlib import Path

from customtkinter import CTkFrame, CTkLabel, CTkScrollableFrame

from app.api import container
from app.ui import SelectableCanvas


class SelectBlock(CTkFrame):

    def __init__(self, master, path1: str, path2: str, **kwargs):
        super(SelectBlock, self).__init__(master, **kwargs)

        self.l = SelectableCanvas(self, path1)
        self.l.grid(row=0, column=0)

        self.reasons = CTkLabel(self, text='', width=280, wraplength=230,
                                justify="left")
        self.reasons.grid(row=0, column=1)

        self.r = SelectableCanvas(self, path2)
        self.r.grid(row=0, column=2)

        self.pack(pady=5, padx=5)

    def mark_weaker(self):
        table = self.l if self.l.info < self.r.info else self.r
        arguments = table.info._remove_reasons  # noqa

        if table:
            table.choose()

        msg = "● " + "\n● ".join(arguments)
        self.reasons.configure(text=msg)

    def remove(self) -> None:
        for w in (self.l, self.r):
            if not w.is_ignored and w.is_chosen:
                filepath = w.info.path

                try:
                    container.remove_method(filepath)
                    a = (w.info.name, w.info.directory,
                         f'Удаление файла {w.info.path}',
                         f'Удалена копия. {self.reasons["text"]}')
                except Exception as e:
                    a = (w.info.name, w.info.directory, '', e)

        self.pack_forget()


class ScrollableFrame(CTkScrollableFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, width=800, height=600, **kwargs)

        parent = master.master.children
        self.mark = parent['!topframe'].children['!filelist'].mark

    @property
    def _childs(self) -> list[SelectBlock]:
        return self.children.values()  # noqa

    def __mark(self, path: str) -> None:
        if str(Path(path).parent) == container.sort_directory:
            self.mark(os.path.basename(path))

    def fill(self, release_pairs: list[tuple[str, str]]) -> None:
        for img_path_1, img_path_2 in release_pairs:
            with suppress(FileNotFoundError):
                SelectBlock(self, img_path_1, img_path_2)
                self.__mark(img_path_1)
                self.__mark(img_path_2)

    def remove_selected(self) -> None:
        [block.remove() for block in self._childs]

    def smart_mark(self) -> None:
        [block.mark_weaker() for block in self._childs]

    def clear(self) -> None:
        [block.pack_forget() for block in self._childs]

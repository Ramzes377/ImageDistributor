import os

import customtkinter
from customtkinter import CTkFrame, CTkLabel, CTkScrollableFrame

from app.ui.submenu.copy_manager.canvas import SpecialCanvas


class ChooseBlock(CTkFrame):
    equal_msg = ['Предположительно изображения идентичны почти полностью.']

    def __init__(self, master, path1: str, path2: str, **kwargs):
        super(ChooseBlock, self).__init__(master, **kwargs)

        self.l = SpecialCanvas(self, path1)
        self.l.grid(row=0, column=0)

        self.reasons = CTkLabel(self, text='', width=280, wraplength=230,
                                justify="left")
        self.reasons.grid(row=0, column=1)

        self.r = SpecialCanvas(self, path2)
        self.r.grid(row=0, column=2)

        self.pack(pady=5, padx=5)

    def mark_weaker(self):
        score, arguments = self.l.guess_delete(self.r)
        if score[0] == score[1]:
            table = self.l
            arguments = self.equal_msg
        else:
            table = self.l if score[0] > score[1] else self.r

        if table:
            table.choose()

        msg = "● " + "\n● ".join(arguments)
        self.reasons.configure(text=msg)

    def remove(self, left=True):
        w = self.l if left else self.r
        a = ''
        if w.is_chosen:
            filepath = w.path

            try:
                os.remove(filepath)
                a = (w.name, w.directory, f'Удаление файла {w.path}',
                     f'Удалена копия. {self.reasons["text"]}')
            except Exception as e:
                a = (w.name, w.directory, '', e)
        return a


class ScrollableFrame(CTkScrollableFrame):
    container: set[tuple[str, str]] = []   # paths of supposed copies

    def __init__(self, master, **kwargs):
        super().__init__(master, width=800, height=600, **kwargs)

    def release_container(self):

        try:
            for img_path_1, img_path_2 in self.container:
                ChooseBlock(self, img_path_1, img_path_2)

            self.container.clear()
        except RuntimeError:
            self.release_container()

    def smart_remove(self):
        undeleted = []
        while self._set:
            b = self._set.pop()

            if b.l.is_chosen or b.r.is_chosen:
                b.pack_forget()
            else:
                undeleted.append(b)
        self._set.extend(undeleted)

    def smart_mark(self):
        [child.mark_weaker() for child in self.children.values()]

    def clear(self):
        for child in self.children.values():
            child.pack_forget()


if __name__ == '__main__':
    root = customtkinter.CTk()

    root.grid_rowconfigure(0, weight=1)
    root.columnconfigure(3, weight=1)

    frame = ScrollableFrame(root)

    container = []
    for i in range(150):
        container.append(('image.jpg', 'image.jpg'))

    frame.container = container
    frame.release_container()
    frame.pack(fill='both', expand=True, padx=10, pady=10)

    frame.smart_mark()
    root.mainloop()
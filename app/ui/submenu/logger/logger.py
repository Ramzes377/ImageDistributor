import os
import shutil
from contextlib import suppress
from tkinter import Menu, TclError
from tkinter.ttk import Style, Treeview

from app.api import container
from app.ui.submenu.base_window import Window


class LoggerWidget(Window):

    def __init__(self, master):
        super(LoggerWidget, self).__init__(master)

        self.title('Список изменений')

        s = Style(self)
        s.theme_use("clam")
        s.configure(
            'Treeview',
            rowheight=25,
            background='#2d2d30',
            fieldbackground='#2d2d30'
        )
        s.map(
            'Treeview',
            foreground=[("!disabled", 'white')],
            background=[('selected', '#1f1f22')]
        )

        self.back_menu = Menu(self, tearoff=0)
        self.back_menu.add_command(label=f'Вернуть', command=lambda: None)

        self.tree = Treeview(
            self,
            show='headings',
            columns=("Name", "Path", "Action", "Info")
        )

        self.tree.heading("Name", text="Имя файла")
        self.tree.heading("Path", text="Путь")
        self.tree.heading("Action", text="Действие")
        self.tree.heading("Info", text="Доп. информация")

        self.tree.column('Name', anchor='w')
        self.tree.column('Path', anchor='w')
        self.tree.column('Action', anchor='w')
        self.tree.column('Info', anchor='w')

        self.tree.bind("<Button-3>", self.popup)
        self.tree.pack(fill='both', expand=1)

    def __call__(self, a):
        self._last = self.tree.insert('', index='end', values=a)

    def switch_state(self):
        super(LoggerWidget, self).switch_state()

        # previous item deleted or empty logger table
        with suppress(AttributeError, TclError):
            self.tree.see(self._last)

    def back_file(self, file: str, path: str) -> None:
        path = os.path.join(path, file)
        try:
            shutil.move(path, container.directory)
            self.tree.delete(self.tree.selection())
        except Exception as e:
            action = (
                file, path, f'Возврат из {path}', container.directory, e
            )
            self.__call__(action)

    def popup(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            file, _, path = self.tree.item(iid)['values'][:3]
            path = path.split(' ')[-1].strip()
            self.back_menu.entryconfigure(
                0,
                command=lambda: self.back_file(file, path)
            )
            self.back_menu.post(event.x_root, event.y_root)

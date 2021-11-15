import tkinter
import shutil
import os
from tkinter.ttk import Treeview, Style

from widgets.basewidget import BaseWindow


class LoggerWidget(BaseWindow, tkinter.Toplevel):
    _instance = None
    img = None
    def __init__(self, *args, **kwargs):
        self.path = kwargs.pop('path')
        self.config = kwargs.pop('config')
        super(LoggerWidget, self).__init__()

        self.title('Список изменений')

        self._counter = 0

        s = Style(self)
        s.theme_use("clam")
        s.configure('Treeview', rowheight=25, background='#2d2d30',
                    fieldbackground='#2d2d30')
        s.map('Treeview', foreground=[("!disabled", 'white')], background=[('selected', '#1f1f22')])

        self.back_menu = tkinter.Menu(self, tearoff=0)
        self.back_menu.add_command(label=f'Вернуть', command=lambda: None)

        self.tree = Treeview(self, show='headings', columns=("Name", "Path", "Action", "Info"))

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


    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LoggerWidget, cls).__new__(cls)
        return cls._instance

    def switch_state(self):
        super(LoggerWidget, self).switch_state()
        try:
            self.tree.see(self._last)
        except AttributeError:             #empty logger table
            pass
        except tkinter.TclError:           #previous item deleted
            pass

    def back_file(self, file, path):
        cur_path = os.path.join(path, file)
        try:
            shutil.move(cur_path, self.path)
            self.tree.delete(self.tree.selection())
        except Exception as e:
            action = (file, cur_path, f'Возврат из {path}', self.path, e)
            self.__call__(action)

    def popup(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            file, _, path = self.tree.item(iid)['values'][:3]
            path = path.split(' ')[-1].strip()
            self.back_menu.entryconfigure(0, command = lambda: self.back_file(file, path))
            self.back_menu.post(event.x_root, event.y_root)

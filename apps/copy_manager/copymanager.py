import os
from tkinter import Button, Toplevel

from workstuff.globals import get_frame
from widgets.basewidget import BaseWindow
from .archive import Archive
from .copymanager_widget import Scrollable

def im_id(hist, size):
    return int(sum((value * (i % 256) ** 2 for i, value in enumerate(hist)))/(size[0] * size[1]))


class mset(set):
    def add(self, a):
        a = tuple(sorted(a))
        super(mset, self).add(a)


class CopyiesManager(BaseWindow, Toplevel):
    mark_as_copy = unmark_copy = lambda: None

    def __init__(self, *args, **kwargs):
        self.folders = kwargs.pop('folders')
        self.config = kwargs.pop('config')
        self.logger = kwargs.pop('logger')
        super(CopyiesManager, self).__init__(*args, **kwargs)
        kw = {'bg':'#1f1f22', 'fg': 'white', 'bd': 1, 'font': ("Times new Roman", 12, "bold")}

        self.root = args[0]

        self.copy_container = mset()

        self.path = os.path.abspath('/')
        self._archive = Archive(self, self.copy_container)
        self.set_mark_methods = lambda mark, unmark: self._archive.set_mark_methods(mark, unmark)


        nroot = get_frame(text='', root_widget=self, pack_args={'side':'top', 'fill': 'both', 'expand': 1})
        self.scrollable = Scrollable(nroot, self, self.logger)

        self.autochoose = Button(self, text='Автовыделение', command=self.scrollable.smart_mark, **kw)
        self.autochoose.pack(fill='x', side='top', padx = 15, pady = 20)

        self.deletechoosen = Button(self, text='Удалить выделенные', command=self.scrollable.smart_remove, **kw)
        self.deletechoosen.pack(fill='x', side='top', padx=15, pady=20)

        self.title('Управление копиями')
        self.minsize(width=800, height=150)

    def change_dir(self, path, folders):
        self.path = os.path.abspath(path)
        self.folders = folders
        self.copy_container.clear()
        self._start_archive_work()

    def _start_archive_work(self):
        self.scrollable.clear()
        self.autochoose['state'] = 'disabled'
        self.deletechoosen['state'] = 'disabled'
        self._archive(self.folders)

    def quit(self):
        try:
            self._archive.files_loader.filling_cache_thread.kill()
        except AttributeError:
            pass
        try:
            self._archive.files_marker.marking_thread.kill()
        except AttributeError:
            pass
        self._archive.save()
        self._is_hidden = True


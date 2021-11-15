import os
from tkinter import Listbox, Scrollbar, Tk, font, Menu
from workstuff.globals import file_is_image
from functools import partial
from watchdog.events import *


def images_names_generator(path):
    return (filename for filename in os.listdir(path) if file_is_image(filename))

default = {'selectmode': 'single', 'bg': '#2d2d30', 'highlightthickness': 0, 'fg': 'white',
            'selectbackground': '#425575', 'bd': 0, "activestyle": 'none', 'exportselection': False}


class FileList(Listbox):
    _files = []

    def __init__(self, *args, **kwargs):
        self.root = args[0]
        self.path = os.path.abspath(kwargs.pop('path'))

        widget_root = kwargs.pop('widget') or args[0]
        self.pause = kwargs.pop('pause')
        self.copy_container = kwargs.pop('copy_container')
        self.q = kwargs.pop('queue')
        self.update_marks= kwargs.pop('upd')
        self.edit_archive = kwargs.pop('edit')
        kwargs = {**default, **kwargs}
        super(FileList, self).__init__(widget_root, **kwargs)

        y_scrollbar = Scrollbar(widget_root, bg='yellow', troughcolor='red')
        y_scrollbar.pack(side='right', fill='y')
        y_scrollbar.config(command=self.yview, bd = 10, bg='blue')
        self.config(yscrollcommand=y_scrollbar.set)

        self.clear_menu = Menu(self, tearoff=0)
        self.clear_menu.add_command(label=f'Скрыть  файл', command=lambda: None)
        self.clear_menu.add_command(label=f'Удалить файл', command=lambda: None)

        self.bind("<<ListboxSelect>>", self.manual_choose)
        self.bind("<Button-3>", self.rightClick)
        self._manual_choosen = False

        bolded = font.Font(family="Times New Roman", slant='roman') # will use the default font
        self.config(font=bolded)

        self.mark_copies = partial(self.mark, '#fa3973', '#c9ba32')
        self.unmark_copies = partial(self.mark, '#2d2d30', '#425575')

        self._update_files()

        self.pack(side='right', fill='both', expand=1, anchor = 'e')
        self._files_check()

    def get_file_index(self, filename):
        return self.get(0, 'end').index(filename)

    def _update_path(self, path):
        self.path = os.path.abspath(path)
        self._update_files()

    def manual_choose(self, event):
        self.pause.unpause()
        try:
            x = self.curselection()[0]
        except IndexError:
            return
        self._prev_selection = x
        file = self.get(x)
        self.current_file = file
        self._manual_choosen = True

    def _step(self):
        if not self._manual_choosen:
            try:
                x = self.curselection()[0]
            except IndexError:
                return
            if not self._prev_selection is None:
                self.delete(self._prev_selection)
                self.select_set(self._prev_selection)
            self._prev_selection = x
            file = self.get(x)
            self.current_file = os.path.abspath(self.path + '\\' + file)
        self._manual_choosen = False

        if not self.current_file:
            self.select_set(0)
            return self._step()

        return os.path.join(self.path, self.current_file)

    def _update_files(self):
        self.delete(0, 'end')
        self._prev_selection = None
        self.current_file = ''
        self.copy_container.clear()
        for filename in images_names_generator(self.path):
            path = os.path.abspath(self.path + '\\' + filename)
            self.insert('end', filename)
            self.copy_container.append(path)
        self.select_set(0)
        self.pause.unpause()

    def _files_check(self):
        while not self.q.empty():
            self._files.append(self.q.get())
        self.handle_events()
        self.root.after(1500, self._files_check)

    def in_current_directory(self, path):
        return self.path == path

    def handle_events(self):
        while self._files:
            event, file = self._files.pop()
            path, filename = os.path.split(file)

            if self.in_current_directory(path):
                if event is FileCreatedEvent:  # create file
                    if self.size() == 0:
                        self._update_files()
                    else:
                        self.insert('end', filename)
                        self.copy_container.append(file)
                        self.update_marks(file, from_filelist=True)
                elif event is FileDeletedEvent:  # delete file
                    try:
                        index = self.get_file_index(filename)
                    except ValueError:
                        continue
                    self.delete(index)
                    if not self.size():
                        self.pause.unpause()
            else:
                if event is FileCreatedEvent:  # create file
                    self.edit_archive(file, None)
                    self.update_marks(file)
                elif event is FileDeletedEvent:  # delete file
                    self.update_marks(file, deleting=True)
                    self.edit_archive(None, file)

        try:
            self.get_file_index(os.path.split(self.current_file)[1])
        except ValueError:
            self.select_set(0)
            self.pause.unpause()


    def mark(self, bg_c, sbg_c, filename):
        try:
            index = self.get_file_index(filename)
            self.itemconfig(index, bg = bg_c, selectbackground = sbg_c)
        except Exception as e:
            pass

    def rightClick(self, event):
        self.selection_clear(0, 'end')
        self.selection_set(self.nearest(event.y))
        self.activate(self.nearest(event.y))
        x = self.curselection()[0]

        self._prev_selection = x
        filename = self.get(x)

        self.current_file = filename
        self._manual_choosen = True

        self.clear_menu.entryconfigure(0, command=lambda: self.delete(x))
        self.clear_menu.entryconfigure(1, command=lambda: os.remove(os.path.join(self.path, filename)))
        self.clear_menu.post(event.x_root, event.y_root)

if __name__ == '__main__':
    root = Tk()
    fl = FileList(root)
    root.mainloop()

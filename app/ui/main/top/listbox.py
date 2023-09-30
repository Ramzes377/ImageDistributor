import os
from contextlib import suppress
from queue import Queue
from tkinter import Listbox, font, Menu

from customtkinter import CTkScrollbar
from watchdog.events import FileCreatedEvent, FileDeletedEvent
from send2trash import send2trash

from app.api import container, directory_images_gen
from app.ui import Watchdog, QueueMessage

default = dict(
    selectbackground='#425575',
    selectmode='single',
    activestyle='none',
    bg='#2d2d30',
    fg='white',
    highlightthickness=0,
    exportselection=False,
    bd=0,
)


class FileList(Listbox):

    def __init__(self, master, **kwargs):

        self.watchdog = Watchdog(container.directory)
        self.watchdog.start()

        self.copy_container = kwargs.pop('copy_container')
        self.update_image = kwargs.pop('update')

        super(FileList, self).__init__(master, **kwargs | default)

        y_scrollbar = CTkScrollbar(master)
        y_scrollbar.pack(side='right', fill='y')
        y_scrollbar.configure(command=self.yview)
        self.config(yscrollcommand=y_scrollbar.set)

        self.clear_menu = Menu(self, tearoff=0)
        self.clear_menu.add_command(label=f'Скрыть файл', command=lambda: None)
        self.clear_menu.add_command(label=f'Удалить файл', command=lambda: None)

        self.bind("<<ListboxSelect>>", self.update_image_to_selected)
        self.bind("<Button-3>", self._call_submenu)
        self.bind("<Shift-Up>", self.select_next)

        self.config(font=font.Font(size=20))
        self.change_directory()

        self._file_events_loop()

        self.pack(side='right', fill='both', expand=1, anchor='e')

    @staticmethod
    def in_current_directory(path):
        return path == container.directory

    def change_directory(self):
        self.delete(0, 'end')

        for filename in directory_images_gen(container.directory):
            self.insert('end', filename)

        self.watchdog.change_directory(container.directory) # noqa
        self.select_by_index(0)

    def get_file_index(self, filename):
        return self.get(0, 'end').index(filename)

    def get_selected(self) -> str | None:
        with suppress(IndexError):
            return self.get(self.curselection()[-1])

    def update_image_to_selected(self, event=None):
        container.current_image = self.get_selected()
        if container.directory and container.current_image:
            path = os.path.join(container.directory, container.current_image)
            self.update_image(path)

    def select_by_index(self, index: int):
        self.select_set(index)
        self.update_image_to_selected()

    def select_next(self, event=None):
        try:
            index = self.get_file_index(container.current_image)
            self.delete(index)
        except ValueError:
            return

        self.select_by_index(self.nearest(index))

    def _call_submenu(self, event):
        self.selection_clear(0, 'end')
        self.selection_set(self.nearest(event.y))
        self.activate(self.nearest(event.y))
        x = self.curselection()[0]

        self._prev_selection = x
        filename = self.get(x)

        path = os.path.join(container.directory, filename)

        self.clear_menu.entryconfigure(0, command=lambda: self.delete(x))
        self.clear_menu.entryconfigure(1, command=lambda: send2trash(path))
        self.clear_menu.post(event.x_root, event.y_root)

    def _file_events_loop(self):
        copy_manager = self.master.master.children.get('!copymanagerwindow')
        queue: Queue = self.watchdog.q  # noqa
        modified = False

        while not queue.empty():
            message: QueueMessage = queue.get(block=False)
            path, filename = os.path.split(message.path)

            if not self.in_current_directory(path):
                continue

            if message.event_type is FileCreatedEvent:
                self.insert('end', filename)
                modified = True
            elif message.event_type is FileDeletedEvent:
                with suppress(ValueError):
                    index = self.get_file_index(filename)
                    self.delete(index)

        if len(self.get(0, 'end')) == 0:
            self.update_image(None)
        elif not self.curselection():
            self.select_by_index(0)

        if copy_manager and modified:
            copy_manager._begin_fill()  # noqa

        self.after(2000, self._file_events_loop)

    def mark(self, filename):
        self.itemconfig(
            self.get_file_index(filename),
            bg='#fa3973',
            selectbackground='#c9ba32'
        )

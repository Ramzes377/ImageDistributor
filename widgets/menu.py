import os

from tkinter import Menu, filedialog, messagebox as mb

from widgets.move_button import MoveButton
from apps.copy_manager.copymanager import CopyiesManager
from apps.logger import LoggerWidget

from apps.lens_settings.lens_submenu import LensSettings


default = {'bg': '#000099', 'fg': 'white', 'activebackground': '#004c99', 'activeforeground': 'white'}


class CustomMenu(Menu):
    def __init__(self, *args, **kwargs):
        _folders = kwargs.pop('folders')
        self._on_dir_change = kwargs.pop('on_dir_change')
        config = kwargs.pop('config')
        kwargs = {**default, **kwargs}
        super(CustomMenu, self).__init__(*args, **kwargs)
        root = self.root = args[0]

        root.config(menu=self)

        self.cur_path = os.path.abspath('menu/')

        file = Menu(self, tearoff=0)
        self.add_cascade(label='Файл', menu=file)
        file.add_command(label='Открыть', command=self.choose_folder)


        ls = LensSettings(config=config, bg = 'black')
        self.log = LoggerWidget(master = root, path=self.cur_path, config = config)
        self.copyies_manager = CopyiesManager(root, bg = '#1f1f22', folders = _folders, config=config, logger = self.log)


        app_menu = Menu(self, tearoff=0)
        self.add_cascade(label="Средства", menu=app_menu)
        app_menu.add_command(label='Последние действия', command = self.log.switch_state)
        app_menu.add_command(label='Управление копиями', command = self.copyies_manager.switch_state)


        settings = Menu(self, tearoff=0)
        self.add_cascade(label='Настройки', menu=settings)
        settings.add_command(label="Настройки лупы", command=ls.switch_state)


    def choose_folder(self):
        path = filedialog.askdirectory()
        if path and path != self.cur_path:
            answer = mb.askyesno(title="Изменить директорию?")
            if answer == True:
                self.change_folder(path)

    def change_folder(self, path):
        self.cur_path = os.path.abspath(path)
        self._on_dir_change(self.cur_path)
        self.log.path = self.cur_path

    def log_action(self):
        action = MoveButton._lastaction
        if not action is None:
            self.log(action)
            MoveButton._lastaction = None
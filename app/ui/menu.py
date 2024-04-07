import os
import shutil
from contextlib import suppress

from tkinter import Menu, filedialog

from app.api import container, directory_images
from app.ui import LensSettingsWindow, CopyManagerWindow, LoggerWidget


class AppMenu(Menu):
    def __init__(self, master):
        super(Menu, self).__init__(master, widgetName='menu')

        logger = LoggerWidget(master)

        copy_manager = CopyManagerWindow(master, bg='#1f1f22')

        file = Menu(self, tearoff=0)
        file.add_command(label='Открыть', command=self.choose_folder)

        app_menu = Menu(self, tearoff=0)
        app_menu.add_command(label='Последние действия',
                             command=logger.switch_state)
        app_menu.add_command(label='Управление копиями',
                             command=copy_manager.switch_state)
        app_menu.add_command(label='Переместить изображения из загрузок',
                             command=self.transfer_images_from_directories)

        lens_settings = LensSettingsWindow(self, bg='black')

        settings = Menu(self, tearoff=0)
        settings.add_command(label="Настройки лупы",
                             command=lens_settings.switch_state)
        settings.add_command(label="Добавить трансферную папку",
                             command=self.add_transfer_directory)

        self.add_cascade(label='Файл', menu=file)
        self.add_cascade(label="Средства", menu=app_menu)
        self.add_cascade(label='Настройки', menu=settings)

    @staticmethod
    def add_transfer_directory() -> None:
        path = os.path.abspath(filedialog.askdirectory())
        container.transfer_directories.add(path)
        container.save()

    @staticmethod
    def transfer_images_from_directories(paths=None):
        paths = paths or container.transfer_directories
        for path in paths:
            for i, img_name in enumerate(directory_images(path)):
                img_path: str = os.path.join(path, img_name)
                with suppress(shutil.Error):
                    shutil.move(img_path, container.sort_directory)

    def choose_folder(self):
        path = os.path.abspath(filedialog.askdirectory())
        if path != container.sort_directory:
            self.change_directory(path)

    def change_directory(self, path: str):
        self.master.change_directory(path)  # noqa

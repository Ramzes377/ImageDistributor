from functools import partial

from widgets.canvas.customcanvas import ImageCanvas
from widgets.move_button import MoveButton, generate_folders_buttons
from widgets.filelist import FileList
from widgets.menu import CustomMenu
from widgets.pause import Pause
from workstuff.watcher import Watchdog
from workstuff.globals import *


class Interface:
    _quit = False

    def __init__(self, root):
        root.protocol('WM_DELETE_WINDOW', self.quit)
        self.root = root
        self.path = CUR_DIR
        self.pause = Pause(root)

        frame = get_frame('Отправить изображение в папку', pack_args={'side': 'bottom'})

        self.gen_buttons = partial(generate_folders_buttons, pause=self.pause, frame_widget=frame)

        self.buttons = self.gen_buttons(path=self.path)

        self.canvas = ImageCanvas(get_frame('Текущее изображение', pack_args={'expand': True, 'side': 'left'}))

        folders = [f"./{b['text']}" for b in self.buttons] + ['./']

        self.menu = CustomMenu(root, on_dir_change=self.update_path, folders=folders, config=CONFIG)

        self.files = FileList(root, pause=self.pause, path=self.path,
                              widget=get_frame('Список изображений', pack_args={'side': 'right'}),
                              copy_container=self.menu.copyies_manager._archive._container,
                              upd=self.menu.copyies_manager._archive.marking,
                              edit=self.menu.copyies_manager._archive.edit,
                              queue=Watchdog.q)

        self.watchdog = Watchdog(path=self.path)
        self.watchdog.start()

        self.menu.copyies_manager.set_mark_methods(self.files.mark_copies, self.files.unmark_copies)
        self.menu.change_folder(self.path)

    def update_path(self, path):
        self.path = path

        self.watchdog.change_directory(self.path)

        [b.pack_forget() for b in self.buttons]

        self.buttons = self.gen_buttons(path=self.path)

        self.files._update_path(self.path)

        self.menu.copyies_manager.change_dir(path, [f"{self.path}/{b['text']}" for b in self.buttons] + [path])

        CONFIG['last_directory'] = self.path
        save_config()

    def sorting_loop(self):
        while not self._quit:
            self.file = self.files._step()
            try:
                self.canvas.change_image(self.file)
            except AttributeError:
                pass
            MoveButton.wait_for_sort(self.file)
            self.menu.log_action()

    def quit(self):
        self._quit = True
        self.menu.copyies_manager.quit()
        self.pause.unpause()
        save_config()


if __name__ == '__main__':
    UI = Interface(root)
    UI.sorting_loop()

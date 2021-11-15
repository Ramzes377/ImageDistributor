from tkinter import Button, Tk, Menu
import os
import shutil


class MoveButton(Button):
    _current_file = None
    _lastaction = None
    _moved = False
    _last_file = None

    def __init__(self, *args, **kwargs):
        widget_root = kwargs.pop('widget') or args[0]
        pause = kwargs.pop('pause')
        self.path = kwargs.pop('path')

        super(MoveButton, self).__init__(widget_root, **kwargs)
        self.config(command = self._move)

        menu = Menu(self, tearoff=0)
        menu.add_command(label=f'Убрать кнопку', command=self.pack_forget)
        self.bind("<Button-3>", lambda event: menu.post(event.x_root, event.y_root))
        self._init_switcher(pause)

        if self['text']:
            self.pack(fill='x', expand=0)

    def _move(self):
        file_path = MoveButton._current_file
        final_path = os.path.join(self.path, self["text"])
        path, file = os.path.split(file_path)

        try:
            shutil.move(file_path, final_path)
            MoveButton._lastaction = (file, path, f'Перемещение в {final_path}', 'ручное перемещение')
            MoveButton._last_file = os.path.join(final_path, file)
        except Exception as e:
            MoveButton._lastaction = (file, path, '', e)
            if e is shutil.Error:
                os.remove(file_path)

        self.pause.unpause()


    @classmethod
    def _init_switcher(cls, pause):
        if not hasattr(cls, 'pause'):
            cls.pause = pause

    @classmethod
    def wait_for_sort(cls, filename):
        cls._current_file = filename
        try:
            cls.pause.wait_for_unpause()
        except AttributeError:
            return


default = {'bg':'#2d2d30', 'fg': 'white', 'bd': 1, 'font': ("Courier New", 12)}
def generate_folders_buttons(path, frame_widget, pause):
    try:
        folders_in_directory = next(os.walk(path))
        buttons = [MoveButton(text=folder_name, widget = frame_widget, pause = pause, path = path, **default)
                for folder_name in folders_in_directory[1] if not folder_name.startswith('.')]
        return buttons if buttons else [MoveButton(text='', widget=frame_widget, pause=pause, path = path, **default)]
    except StopIteration:
        return [MoveButton(text='', widget=frame_widget, pause=pause, path = path, **default)]

if __name__ == '__main__':
    root = Tk()
    buttons = generate_folders_buttons()
    MoveButton._setfile('XbbOy3PCBqs.jpg')
    root.mainloop()

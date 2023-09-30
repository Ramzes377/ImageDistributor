import os
from tkinter import Canvas

from PIL import ImageTk, Image, ImageOps

from app.api import container, file_is_copy, format_bytes
from app.ui.info_tooltip import CreateToolTip


default = dict(
    relief='ridge',
    bg='#1f1f22',
    highlightthickness=1,
    insertwidth=10,
    bd=0,
)


class SpecialCanvas(Canvas):
    res = (0, 0)
    is_chosen = False

    def __init__(self, master, img_path):
        super(SpecialCanvas, self).__init__(master, **default)

        self.path = img_path

        self.directory, self.name = os.path.split(self.path)
        self.file_size = os.path.getsize(img_path)

        self.tooltip = CreateToolTip(self, self.description)

        self.bind("<Configure>", self._update)
        self.bind('<Button-1>', self.choose)

    @property
    def description(self):
        name = f'Имя файла: {self.name}'
        direction = f'Расположение файла: {self.directory}'
        resolution = f'Разрешение изображения: {self.res[0]}x{self.res[1]}'
        size = f'Размер файла: {format_bytes(self.file_size)}'
        return '\n'.join([name, direction, resolution, size])

    def _update(self, event=None):
        image = Image.open(self.path)
        self.configure(bg=default['bg'])

        if self.is_chosen:
            self.configure(bg='#ff392b')

        resized = ImageOps.contain(image, (self.w, self.h))

        self.res = image.size

        self.tooltip.leave()
        del self.tooltip
        self.tooltip = CreateToolTip(self, self.description)

        # if not save as object member, then garbage collector will erase it
        self.image = ImageTk.PhotoImage(resized)
        self.create_image(self.w / 2 - 1, self.h / 2 + 1, image=self.image)

    @property
    def w(self):
        return self.winfo_width()

    @property
    def h(self):
        return self.winfo_height()

    def choose(self, event=None):
        self.is_chosen = not self.is_chosen
        self._update()

    def guess_delete(self, other):
        priory = [0, 0]
        d = {self.name: [], other.name: []}

        if self.res[0] > other.res[0] and self.res[1] > \
                other.res[1]:
            priory[1] += 4
            d[other.name].append(self._lesser_resolution(other.name))
        elif self.res[0] < other.res[0] and self.res[1] < \
                other.res[1]:
            priory[0] += 4
            d[self.name].append(self._lesser_resolution(self.name))

        if self.directory == container.directory:
            priory[0] += 2
            d[self.name].append(self._in_sort_directory(self.name))
        if other.directory == container.directory:
            priory[1] += 2
            d[other.name].append(self._in_sort_directory(other.name))

        if file_is_copy(self.name):
            priory[0] += 1
            d[self.name].append(self._is_copy_name(self.name))
        if file_is_copy(other.name):
            priory[1] += 1
            d[other.name].append(self._is_copy_name(other.name))

        return priory, d[self.name] if priory[0] > priory[1] else d[other.name]

    @staticmethod
    def _lesser_resolution(name: str):
        return f'У изображения {name} меньше разрешение!'

    @staticmethod
    def _in_sort_directory(name: str):
        return f'Изображение {name} находится в сортировочной дирректории!'

    @staticmethod
    def _is_copy_name(name: str):
        return f'Изображение {name} предположительно является копией!'

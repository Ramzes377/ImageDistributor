import os
import re
from dataclasses import dataclass, field
from tkinter import Canvas

from PIL import ImageTk, Image, ImageOps

from app.constants import constants
from app.api import container
from app.api.utils import sizeof_fmt
from app.ui.mixins import _WidgetSizeMixin
from app.ui.tooltip import CreateToolTip

default = dict(
    relief='ridge',
    bg='#1f1f22',
    highlightthickness=1,
    insertwidth=10,
    bd=0,
)


def file_is_copy(file):
    return re.findall(r'\(\d+\)| — копия', file)


_image_comparsion_weights = {
    'resolution': 7,
    'sort_directory': 5,
    'copy_signature': 3,
}


@dataclass(slots=True)
class ImageInfo:
    path: str
    directory: str = None
    name: str = None
    file_size: float = 0
    resolution: tuple[int, int] = (0, 0)

    _remove_reasons: list = field(default_factory=list)
    __deletion_score: int = 1

    def __post_init__(self):
        self.directory, self.name = os.path.split(self.path)
        self.file_size = os.path.getsize(self.path)

    @property
    def _format_resolution(self) -> str:
        return f'{self.resolution[0]}x{self.resolution[1]}'

    @property
    def description(self) -> str:
        return (f'Имя файла: {self.name}\n'
                f'Расположение файла: {self.directory}\n'
                f'Разрешение изображения: {self._format_resolution}\n'
                f'Размер файла: {sizeof_fmt(self.file_size)}')

    @staticmethod
    def __copy_signature(obj: 'ImageInfo') -> None:
        if file_is_copy(obj.name):
            obj.__deletion_score *= _image_comparsion_weights['copy_signature']
            obj._remove_reasons.append(constants.is_copy_name.format(obj.name))

    @staticmethod
    def __in_sort_directory(obj: 'ImageInfo') -> None:
        if obj.directory == container.sort_directory:
            obj.__deletion_score *= _image_comparsion_weights['sort_directory']
            obj._remove_reasons.append(
                constants.in_sort_directory.format(obj.name)
            )

    def __lesser_resolution(self, other: 'ImageInfo') -> None:
        if self.resolution[0] < other.resolution[0] or \
                self.resolution[1] < other.resolution[1]:
            self.__deletion_score *= _image_comparsion_weights['resolution']
            self._remove_reasons.append(
                constants.lesser_resolution.format(self.name)
            )

    def __lt__(self, other: 'ImageInfo') -> bool:
        items = [self, other]

        list(map(self.__copy_signature, items))
        list(map(self.__in_sort_directory, items))
        self.__lesser_resolution(other)

        if self.__deletion_score == other.__deletion_score:
            self._remove_reasons = other._remove_reasons = [constants.equal_imgs]
            return False

        return self.__deletion_score > other.__deletion_score


class SelectableCanvas(Canvas, _WidgetSizeMixin):

    def __init__(self, master, img_path):
        super(SelectableCanvas, self).__init__(master, **default)

        self.is_chosen = False
        self.is_ignored = False

        self.info = ImageInfo(img_path)
        self.tooltip = CreateToolTip(self, self.info.description)

        self.bind("<Configure>", self._update)
        self.bind('<Button-1>', self.choose)
        self.bind('<Button-3>', self.ignore)

    def _update(self, event=None):
        image = Image.open(self.info.path)
        self.configure(bg=default['bg'])

        if self.is_ignored:
            self.configure(bg='#a959ff')
        elif self.is_chosen:
            self.configure(bg='#ff392b')

        resized = ImageOps.contain(image, (self.w, self.h))

        self.info.resolution = image.size

        self.tooltip.leave()
        del self.tooltip
        self.tooltip = CreateToolTip(self, self.info.description)

        # if not save as object member, then garbage collector will erase it
        self.image = ImageTk.PhotoImage(resized)
        self.create_image(self.w / 2 - 1, self.h / 2 + 1, image=self.image)

    def choose(self, event=None):
        self.is_chosen = not self.is_chosen
        self._update()

    def ignore(self, event=None) -> None:
        self.is_ignored = not self.is_ignored
        self._update()

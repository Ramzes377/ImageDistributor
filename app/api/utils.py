import os
import re
import warnings
from dataclasses import dataclass
from typing import Generator

from contextlib import suppress

import imagehash
from PIL import Image

IMAGE_FORMATS = (
    'jpg',
    'jpeg',
    'png',
    'gif',
    'bmp',
)


def is_image(file_path: str) -> bool:
    return file_path.endswith(IMAGE_FORMATS)


def directory_images_gen(working_directory: str) -> Generator:
    return (file for file in os.listdir(working_directory) if is_image(file))


def directory_full_traversal(working_directory):
    return (
        path
        for address, _, files in os.walk(working_directory)
        for name in files
        if is_image(path := os.path.abspath(os.path.join(address, name)))
    )


def format_bytes(b):
    if b > 2 ** 20:
        return f'{round(b / 2 ** 20, 2)} MB'
    return f'{round(b / 2 ** 10, 1)} KB'


def file_is_copy(file):
    return re.findall(r'\(\d+\)', file)


def file_id(img_path: str) -> str | None:
    with suppress(OSError):
        with Image.open(img_path) as img:
            return str(imagehash.dhash(img, 16))


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args,
                                                                 **kwargs)
        return cls._instances[cls]


@dataclass(frozen=True, slots=True)
class ImageHash:
    path: str
    hash: str


class CustomWarning(Warning):
    default_format = warnings.formatwarning

    @classmethod
    def formatwarning(
            cls: 'CustomWarning',
            msg: str,
            category: Warning,
            filename: str,
            lineno: int,
            file: str = None,
            line: int = None,
            **kwargs
    ):
        return f'{filename}: {lineno}: {msg}\n'


warnings.formatwarning = CustomWarning.formatwarning

import glob
import os
from dataclasses import dataclass, asdict
from typing import Generator, Iterable

image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp',
                    '*.tiff', '*.webp']


def directory_images(directory: str, recursive: bool = False) -> Generator:
    if recursive:
        directory = os.path.join(directory, '**')

    for extension in image_extensions:
        pattern = os.path.join(directory, extension)
        yield from glob.glob(pattern, recursive=recursive)


def hamming2(s1: str, s2: str, difference_limit: int = 17) -> int:
    differences = 0
    for i in range(len(s1)):
        if s1[i] != s2[i]:
            differences += 1
        if differences >= difference_limit:
            return 64
    return differences


def get_similar_naive(
        collection: dict[str, str],
        token: str,
        difference_limit: int = 16
) -> set[str]:
    return {path for path, file_token in collection.items()
            if hamming2(token, file_token) < difference_limit}


def sizeof_fmt(num: float, suffix: str = "B") -> str:
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


class OrderedSet(set):

    def add(self, items: Iterable) -> None:
        frozen_items = tuple(sorted(items))
        super().add(frozen_items)


@dataclass(frozen=True, slots=True)
class ScaleRange:
    from_: int | float
    to: int | float
    resolution: int | float

    dict = asdict


@dataclass(frozen=True, slots=True)
class ScaleSettings:
    name: str
    default: int | float
    range: ScaleRange
    settings_field_name: str

import os
from dataclasses import dataclass, field
from typing import Iterable, Generator
from pathlib import Path

from pydantic import BaseModel, Field

from app.api.utils import directory_images


@dataclass(frozen=True, slots=True)
class ImageHash:
    path: str
    hash: str


class _HashTree(BaseModel):
    """ hash: files of same hash """

    mapped_hashes: dict[str, set[str]] = Field(default_factory=dict)
    subdirs: dict[str, '_HashTree'] = field(default_factory=dict)

    def __get_node(self, parents: Iterable[str]) -> '_HashTree':
        cur = self

        for part in parents:
            cur = cur.subdirs.setdefault(part, _HashTree())

        return cur

    def traverse(self, reverse_mapping: bool = False) -> Generator:

        def _traverse(node: _HashTree, path: str = '') -> Generator:
            if reverse_mapping:
                for hash_, names in node.mapped_hashes.items():
                    for name in names:
                        yield os.path.join(path, name), hash_
            else:
                for hash_, names in node.mapped_hashes.items():
                    for name in names:
                        yield hash_, os.path.join(path, name)

            for part in node.subdirs:
                yield from _traverse(
                    node=node.subdirs[part],
                    path=os.path.join(path, part),
                )

        yield from _traverse(self)

    def add(self, hashes: list[ImageHash]) -> None:

        for image_hash in hashes:
            absolute_path = Path(image_hash.path).absolute()
            *parents, file = absolute_path.parts

            hashing_cls = self.__get_node(parents)
            hashing_cls.mapped_hashes.setdefault(image_hash.hash, set())
            hashing_cls.mapped_hashes[image_hash.hash].add(file)

    def remove_exited(self, directory: str) -> None:

        hashing_node = self.__get_node(Path(directory).parts)

        for hash_, files in hashing_node.mapped_hashes.items():
            cpy_iterable = files.copy()
            for file in cpy_iterable:
                if not os.path.isfile(os.path.join(directory, file)):
                    hashing_node.mapped_hashes[hash_].discard(file)

    @property
    def reverse_cache(self) -> dict:
        return dict(self.traverse(reverse_mapping=True))


class Cache(BaseModel):
    hashes: _HashTree = Field(default_factory=_HashTree)
    reverse_cache: dict = Field(default_factory=dict, exclude=True)

    def add(self, hashes: list[ImageHash]):
        self.hashes.add(hashes)
        self.reverse_cache = self.hashes.reverse_cache

    def load(self, directory: str, rm_exited: bool = True) -> None:
        if rm_exited:
            self.hashes.remove_exited(directory)

        self.reverse_cache = self.hashes.reverse_cache

    def unregistered_images(self, directory: str) -> Generator:
        return (path for path in directory_images(directory, recursive=True)
                if path not in self.reverse_cache)

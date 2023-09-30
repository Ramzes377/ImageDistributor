import os
from collections import defaultdict
from contextlib import suppress
from dataclasses import dataclass, field
from typing import Iterable

from app.api.utils import directory_full_traversal


@dataclass(frozen=True, slots=True)
class ImageHash:
    path: str
    hash: str


def hamming2(s1: str, s2: str) -> int:
    c = 0
    for i in range(len(s1)):
        if s1[i] != s2[i]:
            c += 1
        if c == 17:
            return 64
    return c


def cache_inner_struct():
    return defaultdict(set)


@dataclass(slots=True)
class Cache:
    cache: defaultdict = field(
        default_factory=lambda: defaultdict(cache_inner_struct))
    reverse_cache: dict = field(default_factory=dict)

    def add(self, hashes: list[ImageHash]):
        for image_hash in hashes:
            path, name = os.path.split(image_hash.path)
            self.cache[path][image_hash.hash].add(image_hash.path)
            self.reverse_cache[image_hash.path] = image_hash.hash

    def discard(self, files: Iterable[tuple[str, str]], directory: str):
        for img_id, name in files:
            self.cache[directory][img_id].discard(name)
            with suppress(KeyError):
                path = os.path.join(directory, name)
                self.reverse_cache.pop(path)

    def remove_unregistered(self, directory: str):
        unregistered_images = (
            (_id, file)
            for _id, files in
            self.cache[directory].items()
            for file in files if not os.path.isfile(file)
        )
        self.discard(list(unregistered_images), directory)

    def rebuild_reversed_cache(self, directory: str) -> None:
        for path, cache in self.cache.items():
            for _id, files in cache.items():
                for file in files:
                    img_path = os.path.abspath(os.path.join(path, file))
                    self.reverse_cache[img_path] = _id

    @classmethod
    def from_json(cls, data) -> 'Cache':
        instance = cls()

        cache = data.get('cache', {})
        for path, items in cache.items():
            for token, img_paths in items.items():
                instance.cache[path][token] = set(img_paths)

        return instance

    def unregistered_images(self, directory: str):
        return (
            path
            for path in directory_full_traversal(directory)
            if path not in self.reverse_cache
        )

    def subpaths(self, directory: str) -> list[str]:
        return [path for path in self.cache if
                path.startswith(directory)]

    @staticmethod
    def get_similar_naive(
        collection: dict[str],
        token: str,
        max_distance: int = 16
    ) -> set[str]:
        return {path for path, file_token in collection.items()
                if hamming2(token, file_token) < max_distance}

    def json(self) -> dict:
        cache = {}
        for path, items in self.cache.items():
            cache[path] = {token: list(paths) for token, paths in
                           items.items() if paths}
        return {'cache': cache}

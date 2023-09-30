import warnings
from multiprocessing.dummy import Pool as ThreadPool
from queue import Queue
from typing import Iterable

from app.api import container
from app.api.__thread import CustomThread
from app.api.utils import file_id, ImageHash

container.load()


class CacheLoader:
    working_threads: list[CustomThread] = []

    to_cache = []
    callback = None

    _counter = None
    _percent = None
    _quantity = None

    @classmethod
    def begin(cls, master, callback, progress_bar):
        cls.callback = callback
        cls.progress_bar = progress_bar
        cls._counter = 0
        cls._percent = 0
        cls._quantity = len(
            list(container.cache.unregistered_images(container.directory))
        )
        warnings.warn(f"Starting hard caching work with {cls._quantity} files!",
                      ResourceWarning)

        cls.working_threads.append(
            CustomThread(
                master,
                target=cls.hashing_handler,
                args=[container.cache.unregistered_images(container.directory)],
                q_handler=cls.get_cache_data,
                final_handler=cls.final
            )
        )

    @staticmethod
    def hashing_handler(gen: Iterable, queue: Queue) -> None:
        def file_id_for_thread(path: str):
            return ImageHash(path=path, hash=file_id(path))

        pool = ThreadPool(24)
        for image_hash in pool.imap_unordered(file_id_for_thread, gen):
            queue.put(image_hash)

        pool.close()
        pool.join()

    @classmethod
    def get_cache_data(cls, image_hash: ImageHash):
        percent = int(cls._counter / cls._quantity * 100)
        if percent != cls._percent:
            cls._percent = percent
            cls.progress_bar.set(percent/100)

        if image_hash.hash is None:
            return

        cls.to_cache.append(image_hash)
        cls._counter += 1

    @classmethod
    def final(cls):
        container.cache.add(cls.to_cache)
        container.save()

        cls.to_cache = []
        cls.callback()

import multiprocessing
from concurrent.futures import ThreadPoolExecutor, wait
from dataclasses import dataclass

import imagehash
from PIL import Image, ImageFile

from app.api import ImageHash, container
from app.api.parallelization.tasks.base import Task
from app.config import logger

ImageFile.LOAD_TRUNCATED_IMAGES = True


@dataclass(eq=False, unsafe_hash=True)
class HashingTask(Task):
    queue: multiprocessing.Queue

    @staticmethod
    def file_id(img_path: str) -> str | None:
        with Image.open(img_path) as img:
            return str(imagehash.dhash(img, 16))

    def file_id_for_thread(self, path: str):
        self.queue.put(
            ImageHash(path=path, hash=self.file_id(path))
        )

    def target(self) -> None:
        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = [
                executor.submit(self.file_id_for_thread, image)
                for image in
                container.cache.unregistered_images(container.sort_directory)
            ]

            done, not_done = wait(futures)
            for future in done:
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Task generated an exception: {e}")

            if not not_done:
                logger.debug("All tasks completed successfully")

        self.queue.put(None)
        container.save()

import multiprocessing
from dataclasses import dataclass
from queue import Empty
from typing import Generator, Callable

from app.api.parallelization.tasks.base import Task
from app.config import logger


@dataclass(eq=False, unsafe_hash=True)
class ProgressTask(Task):
    queue: multiprocessing.Queue
    set_progress: Callable

    def fetch(self) -> Generator:
        while True:
            try:
                percent = self.queue.get(timeout=3)
                yield percent
            except Empty:
                yield None

    def target(self):
        gen = self.fetch()
        while self.running:
            percent = next(gen)
            if percent is None:
                continue

            try:
                logger.debug(f'Hashing percent: {percent}')
                self.set_progress(percent / 100)
                if percent >= 100:
                    return
            except RuntimeError:
                return

            logger.debug(f'{self.name} in event loop.')

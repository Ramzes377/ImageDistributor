import multiprocessing
from dataclasses import dataclass
from queue import Empty
from typing import Callable, Generator

from app.api.parallelization.tasks.base import Task
from app.config import logger


@dataclass(eq=False, unsafe_hash=True)
class InnerFillTask(Task):
    queue: multiprocessing.Queue
    fill_task: Callable

    def fetch(self) -> Generator:
        while True:
            try:
                items = self.queue.get(timeout=3)
                yield items
            except Empty:
                yield None

    def target(self):
        gen = self.fetch()

        while self.running:
            items = next(gen)
            if items is None:
                continue

            try:
                self.fill_task(items)
            except RuntimeError:
                logger.error(f'{self.name} error on fill.')

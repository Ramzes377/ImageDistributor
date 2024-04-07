import multiprocessing
import queue
from dataclasses import dataclass, field
from time import sleep
from typing import Any

from app.api import ImageHash, container
from app.api.parallelization.tasks.base import Task
from app.api.statistics import Statistics
from app.config import logger


@dataclass(eq=False, unsafe_hash=True)
class QueueTask(Task):
    queue: multiprocessing.Queue
    consumer: Any
    producer: Any
    statistics: Statistics = field(default_factory=Statistics, hash=False)

    _BATCH_SIZE: int = 100

    def target(self):
        cache: list[ImageHash] = []
        prev_percent: int = 0

        self.consumer.send(['percent', 0])

        while self.running:
            for _ in range(self._BATCH_SIZE):

                try:
                    item: ImageHash | None = self.queue.get(timeout=1)
                except queue.Empty:
                    continue

                if item is None:
                    container.add_cache(cache)
                    self.consumer.send(['percent', 100])
                    self.producer.send('OUTER_FILL')
                    return

                self.statistics.incr()

                if item.hash is not None:
                    cache.append(item)

            if self.statistics.complete_percent > prev_percent:
                prev_percent = self.statistics.complete_percent
                self.consumer.send(['percent', prev_percent])

            logger.debug(f'{self.name} in event loop.')

            sleep(0.5)

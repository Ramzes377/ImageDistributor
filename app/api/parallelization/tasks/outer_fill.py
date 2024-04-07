import time
from dataclasses import dataclass
from typing import Any

from app.api.container import container
from app.api.utils import directory_images, OrderedSet, get_similar_naive
from app.config import logger
from .base import Task


@dataclass(eq=False, unsafe_hash=True)
class OuterFillTask(Task):
    consumer: Any

    def filling(self, algorithm=get_similar_naive) -> None:
        pairs = OrderedSet()
        begin_time = time.time()

        comparable_files = {path: token for path, token in
                            container.cache.reverse_cache.items()
                            if path.startswith(container.sort_directory)}

        for i, path in enumerate(directory_images(container.sort_directory)):

            if not self.running:
                return

            try:
                _hash = container.cache.reverse_cache[path]
            except KeyError:
                return

            similar = algorithm(comparable_files, _hash)
            similar.remove(path)

            for file in similar:
                pairs.add((path, file))

        elapsed_time = round(time.time() - begin_time, 1)

        self.consumer.send(['fill', pairs])
        logger.info(f'End caching work! Elapsed time: {elapsed_time}')

    def target(self) -> None:
        while self.running:
            if self.consumer.poll(1):
                signal = self.consumer.recv()
                if signal == 'OUTER_FILL':
                    self.filling()

            time.sleep(3)

            logger.debug(f'{self.name} in event loop.')

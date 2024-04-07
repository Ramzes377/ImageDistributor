from dataclasses import dataclass, field
from time import sleep
from typing import Any

from app.api.parallelization.tasks.base import Task
from app.config import logger


@dataclass(eq=False, unsafe_hash=True)
class ProxyTask(Task):
    consumer: Any
    task_transport: dict = field(default_factory=dict, hash=False)

    _loop_idle: int = 0.5

    def target(self, *args, **kwargs) -> None:
        """ Fetch data from process loop and split it into topics. """

        while self.running:
            if self.consumer.poll(1):
                task_name, data = self.consumer.recv()

                task_transport = self.task_transport.get(task_name)
                if task_transport is not None:
                    task_transport.put(data)

            sleep(self._loop_idle)

            logger.debug(f'{self.name} in event loop.')

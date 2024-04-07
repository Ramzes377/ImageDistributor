from dataclasses import dataclass

from app.config import logger
from ..tasks import Task


@dataclass
class Pipe:
    tasks: list[Task]

    is_running: bool = False

    def run(self) -> None:
        for task in self.tasks:
            task.start()

        self.is_running = True

    def stop(self) -> None:
        logger.debug(f'{self.__class__.__name__} in stop.')
        for task in self.tasks:
            task.stop()

        self.is_running = False

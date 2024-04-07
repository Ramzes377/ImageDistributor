import multiprocessing
from time import sleep

from app.config import logger
from .pipes import Pipe, HashingPipe
from .tasks import _StopBase


class BackgroundWorker(_StopBase, multiprocessing.Process):
    _loop_idle: int = 5
    _pipes: list[Pipe] = None

    def __init__(
            self,
            task_transport: dict[str, multiprocessing.Queue] = None,
    ) -> None:
        _StopBase.__init__(self)
        multiprocessing.Process.__init__(self)

        self.task_transport = task_transport
        self.consumer, self.producer = multiprocessing.Pipe(duplex=True)

    def run(self):
        """ Objects attached only to proccess. """

        self._pipes = [
            HashingPipe(
                consumer=self.consumer,
                producer=self.producer,
                task_transport=self.task_transport,
            ),
        ]

        self._loop()

    def add_tasks(self, *task_names: str) -> None:
        """ Add outer tasks to execute in background process. """

        for task in task_names:
            self.producer.send(task)

    def _loop(self) -> None:
        running_pipes: list[Pipe] = []

        while self.running:
            pipes_ = self._pipes.copy()
            for pipe in pipes_:
                pipe.run()
                running_pipes.append(pipe)
                self._pipes.pop(0)

            sleep(self._loop_idle)

            logger.debug(f'{self.name} in event loop.')

        for pipe in running_pipes:
            pipe.stop()

        logger.debug(f'{self.name} stopped.')

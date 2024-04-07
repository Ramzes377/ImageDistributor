import multiprocessing
from dataclasses import dataclass, field
from typing import Any

from .base import Pipe
from ..tasks import Task, ProxyTask, OuterFillTask, HashingTask, QueueTask


@dataclass(kw_only=True)
class HashingPipe(Pipe):
    consumer: Any
    producer: Any
    task_transport: dict

    queue: multiprocessing.Queue = field(default_factory=multiprocessing.Queue)

    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.tasks = [
            QueueTask(
                queue=self.queue,
                consumer=self.consumer,
                producer=self.producer,
            ),
            ProxyTask(
                consumer=self.producer,
                task_transport=self.task_transport,
            ),
            HashingTask(queue=self.queue),
            OuterFillTask(consumer=self.consumer),
        ]

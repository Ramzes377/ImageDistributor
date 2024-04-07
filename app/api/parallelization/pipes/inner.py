from dataclasses import dataclass, field
from typing import Callable

from .base import Pipe
from ..tasks import Task, InnerFillTask, ProgressTask


@dataclass(kw_only=True)
class InnerPipe(Pipe):
    task_transport: dict

    set_progress: Callable
    fill_task: Callable

    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.tasks = [
            ProgressTask(
                queue=self.task_transport['percent'],
                set_progress=self.set_progress,
            ),
            InnerFillTask(
                queue=self.task_transport['fill'],
                fill_task=self.fill_task,
            ),
        ]

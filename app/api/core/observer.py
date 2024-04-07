from queue import Queue
from dataclasses import dataclass
from typing import Type

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer


@dataclass
class QueueMessage:
    event_type: Type[FileSystemEvent]
    path: str


class Watchdog(FileSystemEventHandler, Observer):
    q = Queue()

    def __init__(self, path):
        super(Watchdog, self).__init__()
        self.watcher = self.schedule(self, path=path, recursive=True)

    def change_directory(self, path: str) -> None:
        self.unschedule(self.watcher)
        self.watcher = self.schedule(self, path=path, recursive=True)

    def on_any_event(self, event: FileSystemEvent) -> None:
        self.q.put(
            QueueMessage(event_type=type(event), path=event.src_path),
        )

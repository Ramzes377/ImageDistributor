from queue import Queue
from dataclasses import dataclass

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

from app.api.utils import is_image


@dataclass
class QueueMessage:
    event_type: FileSystemEvent
    path: str


class Watchdog(FileSystemEventHandler, Observer):
    q = Queue()

    def __init__(self, path):
        super(Watchdog, self).__init__()
        self.watcher = self.schedule(self, path=path, recursive=True)

    def change_directory(self, path: str):
        self.unschedule(self.watcher)
        self.watcher = self.schedule(self, path=path, recursive=True)

    def on_any_event(self, event: FileSystemEvent):
        if is_image(event.src_path):
            msg = QueueMessage(event_type=type(event), path=event.src_path)
            self.q.put(msg)

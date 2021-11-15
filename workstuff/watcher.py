from watchdog.observers import Observer
from queue import Queue
from workstuff.globals import file_is_image
from watchdog.events import FileSystemEventHandler


class Watchdog(FileSystemEventHandler, Observer):
    q = Queue()
    def __init__(self, path):
        super(Watchdog, self).__init__()
        self.watcher = self.schedule(self, path=path, recursive=True)

    def change_directory(self, path):
        self.unschedule(self.watcher)
        self.watcher = self.schedule(self, path=path, recursive=True)

    def on_any_event(self, event):
        if file_is_image(event.src_path):
            self.q.put((type(event), event.src_path))

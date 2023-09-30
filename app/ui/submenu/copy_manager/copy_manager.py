import os
import time
import warnings
from threading import Thread

from customtkinter import CTkButton, CTkFrame, CTkProgressBar

from app.api import container, directory_images_gen
from app.ui import Window

from .cache_loader import CacheLoader   # noqa
from .frame import ScrollableFrame  # noqa


class PairsContainer(set):

    def add(self, pair: tuple) -> None:
        pair = tuple(sorted(pair))
        super().add(pair)


class CopyManagerWindow(Window):
    _is_hidden = True

    def __init__(self, master, **kwargs):
        super(CopyManagerWindow, self).__init__(master, **kwargs)

        self.copy_container = set()

        self.mark = master.children['!topframe'].children['!filelist'].mark

        self.scrollable = ScrollableFrame(self)
        self.scrollable.pack(fill='both', expand=True, padx=10, pady=10)

        frame = CTkFrame(self)
        frame.pack(side='bottom', fill='x')

        self.auto = CTkButton(frame, text='Авто выделение',
                              command=self.scrollable.smart_mark)
        self.auto.pack(fill='x', side='left', padx=15, pady=20)

        self.delete = CTkButton(frame, text='Удалить выделенные',
                                command=self.scrollable.smart_remove)
        self.delete.pack(fill='x', side='right', padx=15, pady=20)

        self.progress_bar = CTkProgressBar(frame, mode="determinate")
        self.progress_bar.pack(fill='x', expand=1, padx=60, pady=20)
        self.progress_bar.set(0)

        CacheLoader.begin(master, self.fill_container, self.progress_bar)

        self.title('Управление копиями')
        self.protocol('WM_DELETE_WINDOW', self.switch_state)
        self.minsize(width=800, height=150)

    def _begin_fill(self):
        self.progress_bar.set(0)

        fill_thread = Thread(
            target=self.fill_container,
            args=[],
        )

        CacheLoader.begin(self, fill_thread.start, self.progress_bar)

    def change_directory(self, path: str) -> None:
        self.scrollable.clear()

        self.auto['state'] = 'disabled'
        self.delete['state'] = 'disabled'

        self._begin_fill()

    def fill_container(self, algorithm=container.cache.get_similar_naive):
        pairs = PairsContainer()
        to_mark = set()

        begin_time = time.time()

        comparable_files = {path: token for path, token in
                            container.cache.reverse_cache.items()
                            if path.startswith(container.directory)}

        items = list(directory_images_gen(container.directory))

        for i, name in enumerate(items):
            path = os.path.join(container.directory, name)

            try:
                _hash = container.cache.reverse_cache[path]
            except KeyError:
                return

            similar = algorithm(comparable_files, _hash)

            for file in similar:
                if path == file:
                    continue

                pairs.add((path, file))
                if container.directory in file:
                    to_mark.add(name)

        msg = f"End caching work! Elapsed time: {(time.time() - begin_time):.2f}"
        warnings.warn(msg, ResourceWarning)
        truncated = pairs
        self.scrollable.container = truncated
        self.scrollable.release_container()
        list(map(self.mark, to_mark))

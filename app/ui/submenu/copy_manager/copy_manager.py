import multiprocessing

from customtkinter import CTkButton, CTkFrame, CTkProgressBar

from app.api.parallelization.background_worker import BackgroundWorker
from app.api.parallelization.pipes.inner import InnerPipe
from app.ui import Window

from .frame import ScrollableFrame


class CopyManagerWindow(Window):
    interested_topics = ['percent', 'fill']

    def __init__(self, master, **kwargs):
        super(CopyManagerWindow, self).__init__(master, **kwargs)

        self.scrollable = ScrollableFrame(self)
        self.scrollable.pack(fill='both', expand=True, padx=10, pady=10)

        frame = CTkFrame(self)
        frame.pack(side='bottom', fill='x')

        self._build_buttons(frame)

        progress_bar = CTkProgressBar(frame, mode="determinate")
        progress_bar.pack(fill='x', expand=1, padx=60, pady=20)
        progress_bar.set(0)

        self._set_progress = progress_bar.set

        self.task_transport: dict[str, multiprocessing.Queue] = {
            topic: multiprocessing.Queue()
            for topic in self.interested_topics
        }

        self.worker = BackgroundWorker(task_transport=self.task_transport)
        self.worker.start()
        self.worker.add_tasks('fill')

        self.inner_pipe = InnerPipe(
            task_transport=self.task_transport,
            set_progress=self._set_progress,
            fill_task=self.scrollable.fill,
        )
        self.inner_pipe.run()

        self.title('Управление копиями')
        self.protocol('WM_DELETE_WINDOW', self.switch_state)
        self.minsize(width=800, height=150)

    def _build_buttons(self, frame: CTkFrame) -> None:
        self.auto = CTkButton(frame, text='Авто выделение',
                              command=self.scrollable.smart_mark)
        self.auto.pack(fill='x', side='left', padx=15, pady=20)

        self.delete = CTkButton(frame, text='Удалить выделенные',
                                command=self.scrollable.remove_selected)
        self.delete.pack(fill='x', side='right', padx=15, pady=20)

    def destroy(self):
        self.inner_pipe.stop()
        self.worker.stop()

        super().quit()

    def change_directory(self, path: str) -> None:
        self.scrollable.clear()

        self.auto['state'] = 'disabled'
        self.delete['state'] = 'disabled'

        self._set_progress(0)

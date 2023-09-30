import ctypes
from multiprocessing.dummy import Queue
from threading import Thread
from typing import Callable


class CustomThread(Thread):
    def __init__(self, master, target, args, q_handler, final_handler,
                 exclude_args=False):

        self.master = master

        self.queue_handler = q_handler
        self.final_handler = final_handler

        self.q = Queue()

        args = list(args)
        if not exclude_args:
            args += [self.q]

        super(CustomThread, self).__init__(target=target, args=args)

        self.start()
        self.thread_maintenance()

    def queue_loop(self, handler: Callable = None):

        handler = handler or self.queue_handler

        while not self.q.empty():
            handler(self.q.get())

    def thread_maintenance(self):
        self.queue_loop()

        if self.is_alive():
            self.master.after(50, self.thread_maintenance)
        else:
            self.join()
            self.final_handler()

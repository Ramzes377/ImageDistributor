from multiprocessing.dummy import Queue
from threading import Thread

class BaseThread:
    def __init__(self, parent, thread_handler, thread_args, q_handler, final_handler):

        self.parent = parent
        self.queue_handler = q_handler
        self.final_handler = final_handler

        self.q = Queue()

        thread_args = list(thread_args) + [self.q]

        self.process = Thread(target=thread_handler, args=thread_args)
        self.process.start()

        self.thread_maintenance()


    def queue_loop(self, handler = None):
        handler = self.queue_handler if not handler else handler
        while not self.q.empty():
            handler(self.q.get())

    def thread_maintenance(self):
        self.queue_loop()
        if self.process.is_alive():
            self.parent.after(2000, self.thread_maintenance)
        else:
            self.final_handler()
            self.kill()

    def is_alive(self):
        return self.process.is_alive()

    def kill(self, timeout = 1):
        try:
            self.process.join(timeout=timeout)
            self.process._stop()
        except Exception as e:
            pass

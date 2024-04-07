import time

from app.api.parallelization.background_worker import WorkerBuilder


def dummy_task() -> None:
    time.sleep(5)


def test_worker():
    with WorkerBuilder() as worker:
        worker.add_tasks('dummy234')

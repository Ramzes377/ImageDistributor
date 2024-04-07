import functools
import multiprocessing
from abc import abstractmethod
from dataclasses import dataclass
from threading import Thread
from typing import Callable

from app.config import logger


class _StopBase:
    _running: multiprocessing.Event = None

    def __init__(self, *args, **kwargs) -> None:
        self._running = multiprocessing.Event()
        self._running.set()

    def stop(self) -> None:
        self._running.clear()

    @property
    def running(self) -> bool:
        return self._running.is_set()

    @property
    def stopped(self) -> bool:
        return not self.running


class _BaseThread(Thread):

    @abstractmethod
    def target(self):
        ...


class LoggingTargetMeta(type):
    @staticmethod
    def __logging_decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            logger.debug(f'{self.name} start event loop.')
            result = func(self, *args, **kwargs)
            logger.info(f'{self.name} end event loop.')
            return result

        return wrapper

    def __new__(cls, name, bases, dct):
        if 'target' in dct:
            original_method = dct['target']
            dct['target'] = cls.__logging_decorator(original_method)
        return super(LoggingTargetMeta, cls).__new__(cls, name, bases, dct)


@dataclass(eq=False, unsafe_hash=True)
class Task(_StopBase, _BaseThread, metaclass=LoggingTargetMeta):
    def __post_init__(self):
        _StopBase.__init__(self)
        _BaseThread.__init__(self, target=self.target)

    @property
    def name(self) -> str:
        return self.__class__.__name__

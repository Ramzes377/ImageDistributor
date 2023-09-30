from tkinter import Scale, DoubleVar, IntVar
from typing import Callable

from customtkinter import CTkLabel

from app.ui.main.top.zoom.utils import SliderSettings


class LensState(IntVar):
    previous_value: DoubleVar = None

    def __init__(self, *args, **kwargs):
        super(LensState, self).__init__(*args, **kwargs)
        self.previous_value = self.get()

    def _is_change(self) -> bool:
        return self.previous_value != self.get()

    def back_previous(self) -> None:
        self.set(self.previous_value)

    def save_previous(self) -> None:
        self.previous_value = self.get()


class SpecialSlider(Scale):
    value: DoubleVar = None
    previous_value: DoubleVar = None

    def __init__(
            self,
            master,
            callback: Callable,
            settings: SliderSettings,
    ):
        self._callback = callback
        self.previous_value = settings.default
        self.value = DoubleVar()

        label = CTkLabel(
            master,
            text=settings.name,
            font=("Times new Roman", 15, "bold")
        )
        label.pack(fill='both')

        super(SpecialSlider, self).__init__(
            master,
            command=self.edit,
            variable=self.value,
            orient='horizontal',
            **settings.range.dict()
        )

        self.set(self.previous_value)
        self.pack(fill='both')

    def _get(self) -> float:
        return self.value.get()

    def _is_change(self) -> bool:
        return self.previous_value != self._get()

    def edit(self, val) -> None:
        self.value.set(val)
        self._callback()

    def back_previous(self) -> None:
        self.value.set(self.previous_value)
        self.set(self.previous_value)

    def save_previous(self) -> None:
        self.previous_value = self._get()

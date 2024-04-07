from dataclasses import dataclass, field
from tkinter import Scale, DoubleVar, StringVar
from typing import Callable, Any

from customtkinter import CTkLabel

from app.api.core import metric_mapping
from app.api.utils import ScaleSettings


class LensMode(StringVar):

    def get(self) -> str:
        value = super(LensMode, self).get()
        return metric_mapping.get(value, value)


@dataclass
class CustomScale(Scale):
    master: Any
    callback: Callable
    settings: ScaleSettings
    value: DoubleVar = field(default_factory=DoubleVar)

    def edit(self, val) -> None:
        self.value.set(val)
        self.callback()

    def __post_init__(self):
        CTkLabel(
            master=self.master,
            text=self.settings.name,
            font=("Times new Roman", 15, "bold"),
        ).pack(fill='both')

        super(CustomScale, self).__init__(
            master=self.master,
            command=self.edit,
            variable=self.value,
            orient='horizontal',
            **self.settings.range.dict(),
        )

        self.set(self.settings.default)
        self.pack(fill='both')

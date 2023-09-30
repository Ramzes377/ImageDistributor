from functools import partial
from typing import Generator

from PIL import ImageTk
from customtkinter import CTkCanvas, CTkRadioButton, CTkFrame

from app.ui.submenu.base_window import Window
from .modes import DistanceMode
from .slider import SpecialSlider, LensState
from .utils import SliderSettings, SliderRange


class LensSettingsWindow(Window):
    def __init__(self, master, lens, **kwargs):
        super(LensSettingsWindow, self).__init__(master, **kwargs)

        self.c = CTkCanvas(self, width=500, height=500, highlightthickness=0,
                           bg='black')
        self.c.pack(side='left', expand=1)

        frame = CTkFrame(self)
        frame.pack(side='right')

        self.lens = lens
        self.lens_state = LensState()
        self.lens_state.set(0)

        [CTkRadioButton(frame, text=text, variable=self.lens_state, value=v)
         .pack(anchor='center')
         for v, text in enumerate(DistanceMode)]

        self._scales = [self.lens_state]
        slider = partial(SpecialSlider, frame, self._redraw)
        for settings in (
                SliderSettings('Диаметр лупы', 300,
                               range=SliderRange(10, 500, 2)),
                SliderSettings('Соотношение радиуса', 0.66,
                               range=SliderRange(0, 1, 0.01)),
                SliderSettings('Начальная непрозрачность (%)', 88,
                               range=SliderRange(10, 100, 1)),
                SliderSettings('Конечная непрозрачность (%)', 5,
                               range=SliderRange(0, 10, 1))
        ):
            self._scales.append(slider(settings))

        self.title('Настройки лупы')

    def _redraw(self):
        self.lens(self.scales_vals)
        self.mask = self.lens.mask
        self._img = ImageTk.PhotoImage(self.mask)
        self.c.create_image(250, 250, image=self._img)

    def _is_scales_change(self) -> bool:
        return any(scale.is_change() for scale in self._scales)

    def save_scales(self) -> None:
        [scale.save_previous() for scale in self._scales]

    def back_previous(self) -> None:
        [scale.back_previous() for scale in self._scales]

    @property
    def scales_vals(self) -> Generator:
        return (scale.get() for scale in self._scales)

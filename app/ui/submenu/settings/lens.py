from functools import partial

from PIL import ImageTk
from customtkinter import CTkCanvas, CTkRadioButton, CTkFrame

from app.api import container
from app.api.core import metrics
from app.api.utils import ScaleSettings, ScaleRange
from app.ui import Window

from .slider import CustomScale, LensMode


class LensSettingsWindow(Window):
    def __init__(self, master, **kwargs):
        super(LensSettingsWindow, self).__init__(master, **kwargs)

        self.c = CTkCanvas(self, width=500, height=500, highlightthickness=0,
                           bg='black')
        self.c.pack(side='left', expand=1)

        frame = CTkFrame(master=self)
        frame.pack(side='right')

        self._build_scales(master=frame)

        self.title('Настройки лупы')

    def _build_scales(self, master: CTkFrame) -> None:
        settings = container.lens_settings

        lens_state = LensMode()
        lens_state.set(settings.mode)

        btn = partial(CTkRadioButton, master, variable=lens_state)
        [btn(text=text, value=text).pack(anchor='center') for text in metrics]

        self._scales = {'mode': lens_state}
        slider = partial(CustomScale, master=master, callback=self._redraw)
        for scale in (
                ScaleSettings(name='Диаметр лупы', default=settings.diameter,
                              range=ScaleRange(10, 500, 2),
                              settings_field_name='diameter'),
                ScaleSettings('Соотношение радиуса', settings.ratio,
                              range=ScaleRange(0, 1, 0.01),
                              settings_field_name='ratio'),
                ScaleSettings('Начальная непрозрачность (0 - 255)',
                              default=settings.inner_brightness,
                              range=ScaleRange(0, 255, 1),
                              settings_field_name='inner_brightness'),
                ScaleSettings('Конечная непрозрачность (0 - 255)',
                              default=settings.outer_brightness,
                              range=ScaleRange(0, 255, 1),
                              settings_field_name='outer_brightness')
        ):
            self._scales[scale.settings_field_name] = slider(settings=scale)

    def _redraw(self) -> None:
        container.lens_settings.__init__(**self.scales_vals)
        self.mask = container.lens_settings.mask
        self._img = ImageTk.PhotoImage(self.mask)
        self.c.create_image(250, 250, image=self._img)

    @property
    def scales_vals(self) -> dict:
        return {name: scale.get() for name, scale in self._scales.items()}

    def hide(self) -> None:
        super(LensSettingsWindow, self).hide()
        container.save()

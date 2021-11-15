from tkinter import Toplevel, Canvas, Radiobutton, Button, IntVar, messagebox as mb
from functools import partial
from PIL import ImageTk

from apps.lens_settings.slider import SpecialSlider
from widgets.basewidget import BaseWindow
from widgets.canvas.lens.lens import lens
from workstuff.globals import get_frame, CONFIG


class lensmode(IntVar):
    def __init__(self, *args, **kwargs):
        super(lensmode, self).__init__(*args, **kwargs)
        self._prev = self.get()

    def _set_prev(self):
        self.set(self._prev)

    def is_change(self):
        return self._prev != self.get()

    def _save_prev(self):
        self._prev = self.get()


class LensSettings(BaseWindow, Toplevel):
    def __init__(self, *args, **kwargs):
        self.config = kwargs.pop('config')
        super(LensSettings, self).__init__(*args[1:], **kwargs)

        self.c = Canvas(self, width=500, height=500, bg='black', highlightthickness=0)
        self.c.pack(side='left', expand=1)

        frame = get_frame('Основные настройки', self)
        self.lens_mode = lensmode()
        params = {'bg': '#1f1f22', 'fg': 'white', 'selectcolor': 'black', 'command': self._redraw}
        modes = ('Круглый', 'Квадратный', 'Смешанный', 'ПсевдоКруглый', 'Ромбовидный', 'Звезда')
        [Radiobutton(frame, text=txt, variable=self.lens_mode, value=i, **params).pack(anchor='center')
         for i, txt in enumerate(modes)]
        self.lens_mode.set(0)

        slider = partial(SpecialSlider, frame, self._redraw)
        sliders_settings = [(300, 'Диаметр лупы', (10, 500, 2)), (0.66, 'Соотношение радиуса', (0, 1, 0.01)),
                            (88, 'Начальная непрозрачность (%)', (10, 100, 1)), (5, 'Конечная непрозрачность (%)', (0, 10, 1))]

        self._scales = [self.lens_mode]
        self._scales += [slider(*a) for a in sliders_settings]

        save_button = Button(frame, text='Сохранить', command=self._save_settings)
        save_button.pack(side='bottom', fill='x')

        if CONFIG.get('lens_parameters'):
            for val, scale in zip(CONFIG['lens_parameters'], self._scales):
                scale._prev = val
                scale._set_prev()
        self.title('Настройки лупы')

    def _redraw(self):
        lens(self.scales_vals)
        self.mask = lens._mask
        self._img = ImageTk.PhotoImage(self.mask)
        self.c.create_image(250, 250, image=self._img)

    def _save_settings(self):
        super(LensSettings, self).switch_state()
        lens(self.scales_vals)
        self._save_vals()
        CONFIG['lens_parameters'] = tuple(self.scales_vals)

    def _any_scale_change(self):
        return any((scale.is_change() for scale in self._scales))

    def switch_state(self):
        super(LensSettings, self).switch_state()
        if self._is_hidden:
            if self._any_scale_change():
                answer = mb.askyesno(title="Внимание", message="Сохранить внесенные в настройки линзы изменения?")
                if answer == True:
                    self._save_settings()
                else:
                    self._back_to_prev()
                lens(self.scales_vals)

                super(LensSettings, self).switch_state()

    def _save_vals(self):
        [scale._save_prev() for scale in self._scales]

    def _back_to_prev(self):
        [scale._set_prev() for scale in self._scales]

    @property
    def scales_vals(self):
        return (scale.get() for scale in self._scales)

from tkinter import Scale, DoubleVar, Label

class SpecialSlider(Scale):
    def __init__(self, root, handler, default, txt, _range):
        self._handler = handler
        self._prev = round(default, 2)
        self.val = DoubleVar()

        label = Label(root, text=txt, font=("Times new Roman", 15, "bold"), bg='#1f1f22', bd=10, fg='white')
        label.pack(fill='both')

        kw = dict(zip(('from_', 'to', 'resolution'), _range))
        kw['orient'] = 'horizontal'
        kw['command'] = self._scale
        kw['variable'] = self.val
        super(SpecialSlider, self).__init__(root, **kw)
        self.set(self._prev)
        self.pack(fill='both')

    def get(self):
        return self.val.get()

    def _scale(self, val):
        self.val.set(val)
        self._handler()

    def _set_prev(self):
        self.val.set(self._prev)
        self.set(self._prev)

    def is_change(self):
        return self._prev != self.get()

    def _save_prev(self):
        self._prev = self.get()

import tkinter.ttk as ttk
from tkinter import Label

s = ttk.Style()
s.theme_names()
s.theme_use('clam')
TROUGH_COLOR = 'blue'
BAR_COLOR = 'green'
c = ['gray', 'white', '#1f1f22', 'yellow', 'orange', 'brown']
s.configure("TProgressbar", troughcolor=c[0],
                bordercolor=c[1], background=c[2], lightcolor=c[3],
                darkcolor=c[4])

class bar:

    def __init__(self, parent):
        self.parent = parent
        self.bar = ttk.Progressbar(parent, mode="determinate", style="TProgressbar")
        self.label = Label(parent, fg='white', bg='#1f1f22', justify='center', font=("Times new Roman", 15, "bold"))
        self._hidden = True

    def __call__(self, n):
        self.set(0)
        if n > 0:
            self.show()
            self.bar["maximum"] = n
            self._percent = int(n/100) if n > 100 else int(100/n)
        else:
            self.hide()

    def set(self, index):
        if self._hidden:
            self.show()
        self.bar['value'] = index
        self.label['text'] = f'{index}/{self.bar["maximum"]}'
        self.parent.update()

    def set_percent(self, percent):
        p = int(percent/100 * self.bar['maximum'])
        self.set(p)
        if percent >= 100:
            self.hide()

    def hide(self):
        self.label.pack_forget()
        self.bar.pack_forget()
        self._hidden = True

    def show(self):
        self.bar.pack(fill = 'x', side='bottom', padx = 50)
        self.label.pack(side='bottom', pady = 10)
        self._hidden = False
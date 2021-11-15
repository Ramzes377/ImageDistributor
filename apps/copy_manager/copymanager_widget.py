from tkinter import Frame, Scrollbar, Canvas, Label, Toplevel
from PIL import Image, ImageTk

from widgets.canvas.customcanvas import BaseCanvas

import numpy as np
import os
import re
import PIL.ImageOps


class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 350   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x, y, cx, cy = self.widget.bbox("all")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()

format_bytes = lambda b: f'{round(b/2**20, 2)} MB' if b > 2**20 else f'{round(b/2**10, 1)} KB'
file_is_copy = lambda file: re.findall(r'\(\d+\)', file)  # check for file is copy

default = {'bg': '#1f1f22', 'bd': 0, 'highlightthickness': 1, 'relief': 'ridge', 'insertwidth': 10}

trash_im = Image.open('./icons/trash.png').convert('RGBA').resize((64, 64))
r, g, b, a = trash_im.split()
rgb_image = Image.merge('RGB', (r, g, b))
inverted_image = PIL.ImageOps.invert(rgb_image)
r2, g2, b2 = inverted_image.split()
reversed_trash_im = Image.merge('RGBA', (r2, g2, b2, a))


class SpecialCanvas(BaseCanvas):

    def __init__(self, parent, img_path):
        super(SpecialCanvas, self).__init__(parent, **default)
        self.parent = parent

        self._cur_filepath = img_path
        self._original_image = Image.open(self._cur_filepath)

        self.trash_im = trash_im if np.average(np.array(self._original_image)[:64, :64]) > 100 else reversed_trash_im

        self._directory, self._name = os.path.split(self._cur_filepath)
        self._size = os.path.getsize(img_path)
        self._orig_resolution = np.array(self._original_image.size, dtype=np.int)

        r = f'{self._orig_resolution[0]}x{self._orig_resolution[1]}'
        self.description = f'Имя файла: {self._name}\nРасположение файла: {self._directory}\nРазрешение изображения:{r}\nРазмер файла: {format_bytes(self._size)}\n'

        self._switch = False
        self._prev_res = 0, 0

        self.bind("<Configure>", self.resize)
        self.bind('<Button-1>', self.choose)

        CreateToolTip(self, self.description)

        self.update_image(surely=False)

    def update_image(self, surely=True):
        cpy = self._original_image.copy()
        cpy.thumbnail(self._resolution)
        size = cpy.size
        if surely or (self._resolution != self._prev_res).any():
            if self._switch:
                cpy.paste(self.trash_im,  ((size[0] - cpy.size[0]) // 2, (size[1] - cpy.size[1]) // 2), self.trash_im)
            self.tk_img = ImageTk.PhotoImage(cpy)
            self.create_image(self.w / 2 - 1, self.h / 2 + 1, image=self.tk_img)
            self._prev_res = size

    def choose(self, event=None):
        self._switch = not self._switch
        self.update_image()

    def guess_delete(self, other):
        priory = [0, 0]
        d = {self._name: [], other._name: []}

        if (self._orig_resolution > other._orig_resolution).all():
            priory[1] += 3
            d[other._name].append(f'У изображения {other._name} меньше разрешение!')
        elif (self._orig_resolution < other._orig_resolution).all():
            priory[0] += 3
            d[self._name].append(f'У изображения {self._name} меньше разрешение!')

        if self._directory == self.parent.parent.parent.path:
            priory[0] += 2
            d[self._name].append(f'Изображение {self._name} находится в сортировочной дирректории!')
        if other._directory == self.parent.parent.parent.path:
            priory[1] += 2
            d[other._name].append(f'Изображение {other._name} находится в сортировочной дирректории!')

        if file_is_copy(self._name):
            priory[0] += 1
            d[self._name].append(f'Изображение {self._name} предположительно является копией!')
        if file_is_copy(other._name):
            priory[1] += 1
            d[other._name].append(f'Изображение {other._name} предположительно является копией!')

        return priory, d[self._name] if priory[0] > priory[1] else d[other._name]


class ChooseBlock(Frame):
    def __init__(self, *args, **kwargs):
        parent, item1, item2 = args
        super(ChooseBlock, self).__init__(parent, **kwargs)
        self.pack()
        self.parent = parent

        self.l = SpecialCanvas(self, item1)
        self.l.grid(row=0, column=0)

        self.r = SpecialCanvas(self, item2)
        self.r.grid(row=0, column=1)

        self.reasons = Label(self, text='', bg='#1f1f22', fg='white', font=("Times new Roman", 12, "bold"), wraplength=450)
        self.reasons.grid(row=0, column=2)

    def mark_weaker(self):
        score, arguments = self.l.guess_delete(self.r)
        if score[0] == score[1]:
            table = self.l
            arguments = ('Предположительно изображения идентичны почти полностью.', )
        else:
            table = self.l if score[0] > score[1] else self.r

        if table:
            table.choose()
            self.reasons['text'] = "\n".join(arguments)

    def remove(self, left=True):
        w = self.l if left else self.r
        a = ''
        if w._switch:
            filepath = w._cur_filepath
            try:
                os.remove(filepath)
                a = (w._name, w._directory, f'Удаление файла {w._cur_filepath}', f'Удалена копия. {self.reasons["text"]}')
            except Exception as e:
                a = (w._name, w._directory, '', e)
        return a


class Scrollable(Frame):
    def __init__(self, frame, parent, logger, width=16):
        self.parent = parent
        self.logger = logger

        self._set = []

        self.scrollbar = scrollbar = Scrollbar(frame, width=width, bg='white')
        scrollbar.pack(side='right', fill='y', expand=False)

        self.canvas = Canvas(frame, yscrollcommand=scrollbar.set, bg='#1f1f22', highlightthickness=0, scrollregion=(0, 0, 4000, 50000))
        self.canvas.pack(side='left', fill='both', expand=True)

        scrollbar.config(command=self.canvas.yview)

        Frame.__init__(self, frame, bg='#1f1f22')

        self.windows_item = self.canvas.create_window(0, 0, window=self, anchor='nw')

        self._copy_container = parent.copy_container

        self.canvas.bind('<Configure>', self.__fill_canvas)
        self.parent.bind("<MouseWheel>", self.scroll)

    def scroll(self, e):
        self.canvas.yview_scroll(int(-e.delta/120), "units")
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def fill_set(self):
        for item1, item2 in self._copy_container:
            if not (os.path.isfile(item1) and os.path.isfile(item2)):
                continue
            c = ChooseBlock(self, item1, item2, bg='#1f1f22')
            self._set.append(c)
        self._copy_container.clear()
        self.update_idletasks()

    def __fill_canvas(self, event):
        self.canvas.itemconfig(self.windows_item, width = event.width)

    def smart_remove(self):
        undeleted = []
        while self._set:
            b = self._set.pop()
            self.logger(b.remove())
            self.logger(b.remove(left=False))

            if b.l._switch or b.r._switch:
                b.pack_forget()
            else:
                undeleted.append(b)
        self._set.extend(undeleted)

    def smart_mark(self):
        [b.mark_weaker() for b in self._set]

    def clear(self):
        while self._set:
            self._set.pop().pack_forget()



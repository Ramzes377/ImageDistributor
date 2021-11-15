from PIL import ImageTk, ImageFilter
from widgets.canvas.lens.lens import lens


class Zoom:

    def __init__(self, parent):
        self.parent = parent
        self._zoomcycle = -1
        self._min_zoom = -2

    def __call__(self):
        self._original_image = self.parent._original_image
        if not self._original_image:
            return

        self._resized_im = self.parent._resized_im
        W, H = self._original_image.size
        self._dt = W/self.parent.w if W > H else H/self.parent.h

        mask, d = lens._mask, lens._diameter
        self._min_zoom = max(d/max(self._original_image.size), 2**.5) - 0.01

        self._zoomcycle = self._min_zoom

        size = self._resized_im.size
        self.top_left_corner = (self.w - size[0])/2, (self.h - size[1])/2
        self.bot_right_corner = (self.w + size[0]) / 2, (self.h + size[1]) / 2

    def zoomer(self, event):
        self._zoomcycle += event.delta/1200
        if self.parent._original_image:
            if self._zoomcycle < self._min_zoom:
                self._zoomcycle = self._min_zoom
            self.crop(event)

    @staticmethod
    def is_cursor_in_pic(crop_area, border, dt):
        return crop_area[0] > -dt and crop_area[1] > -dt and crop_area[2] < border[0] + dt and crop_area[3] < \
               border[1] + dt

    def get_crop_boundary(self, center, d, area, border, dt):
        x, y = center
        nd = min(int(d / self._dt), d)
        r = nd / 2
        if self.top_left_corner[0] > x - r:
            if area[0] < 0:
                area[0] = 0
                area[2] = 2 * dt
            center[0] = self.top_left_corner[0] + r
        elif self.bot_right_corner[0] < x + r:
            if border[0] < area[2]:
                area[0] = border[0] - 2 * dt
                area[2] = border[0]
            center[0] = self.bot_right_corner[0] - r - 1
        if self.top_left_corner[1] > y - r:
            if area[1] < 0:
                area[1] = 0
                area[3] = 2 * dt
            center[1] = self.top_left_corner[1] + r + 1
        elif self.bot_right_corner[1] < y + r:
            if border[1] < area[3]:
                area[1] = border[1] - 2 * dt
                area[3] = border[1]
            center[1] = self.bot_right_corner[1] - r

        return area, nd

    def crop(self, event):
        if not self.parent._original_image:
            return

        self.clear()

        if self._zoomcycle > self._min_zoom:
            self.parent.config(cursor='none')
            x, y = event.x, event.y
            proj_x = (x - self.w / 2 + self._resized_im.size[0] / 2) * self._dt
            proj_y = (y - self.h / 2 + self._resized_im.size[1] / 2) * self._dt

            mask, d = lens._mask, lens._diameter

            dt = d / (self._zoomcycle ** 2)
            area = [proj_x - dt, proj_y - dt, proj_x + dt, proj_y + dt]
            border = self._original_image.size
            if self.is_cursor_in_pic(area, border, dt):
                center = [x, y]
                area, nd = self.get_crop_boundary(center, d, area, border, dt)
                lens_img = self._original_image.crop(area).resize((d, d))

                blured_lens = lens_img.filter(
                    ImageFilter.BoxBlur(radius=0.5 * (self._zoomcycle - self._min_zoom + 0.2) ** 2))
                blured_lens.putalpha(mask)

                self._zimg = ImageTk.PhotoImage(blured_lens.resize((nd, nd)))
                self._zimg_id = self.parent.create_image(*center, image=self._zimg)

                r = int(min(self.w, self.h) / 3)
                self.im = ImageTk.PhotoImage(lens_img.resize((r, r)))
                self.side_crop = self.parent.create_image(self.w - r / 2, self.h - r / 2, image=self.im)
        else:
            self.parent.config(cursor='arrow')

    def clear(self):
        try:
            self.parent.delete(self._zimg_id)
        except AttributeError:
            pass
        try:
            self.parent.delete(self.side_crop)
        except AttributeError:
            pass

    @property
    def w(self):
        return self.parent.w

    @property
    def h(self):
        return self.parent.h
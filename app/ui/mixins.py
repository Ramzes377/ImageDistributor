class _WidgetSizeMixin:
    @property
    def w(self):
        return self.winfo_width()  # noqa

    @property
    def h(self):
        return self.winfo_height()  # noqa

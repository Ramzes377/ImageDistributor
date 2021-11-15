from tkinter import IntVar

class Pause(IntVar):
    def __init__(self, root):
        super(Pause, self).__init__(root)
        self.root = root

    def wait_for_unpause(self):
        self.root.wait_variable(self)

    def unpause(self):
        self.set(1)

    # def __new__(cls, root):
    #     if not hasattr(cls, 'instance'):
    #         cls.instance = super(Pause, cls).__new__(cls)
    #     return cls.instance


if __name__ == '__main__':
    from tkinter import Tk
    root = Tk
    a = Pause(root)